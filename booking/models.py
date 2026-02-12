import uuid
from datetime import datetime, timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from site_settings.models import SiteSettings

from .constants import OCCUPYING_STATUSES, RESERVATION_STATUSES
from .services import is_table_available
from .utils import compute_end_time, get_working_window


class Table(models.Model):
    """Модель стола с вместимостью и состоянием."""
    name = models.CharField('Название', max_length=100)
    capacity = models.PositiveIntegerField('Вместимость')
    is_active = models.BooleanField('Активен', default=True)
    location_note = models.CharField('Примечание', max_length=255, blank=True)

    class Meta:
        """Мета-настройки модели или формы."""
        verbose_name = 'Стол'
        verbose_name_plural = 'Столы'

    def __str__(self) -> str:
        """Возвращает человекочитаемое строковое представление объекта."""
        return self.name


class Reservation(models.Model):
    """Модель бронирования стола с временем и статусом."""
    table = models.ForeignKey(Table, on_delete=models.PROTECT, related_name='reservations')
    date = models.DateField('Дата')
    start_time = models.TimeField('Начало')
    duration_minutes = models.PositiveIntegerField('Длительность (мин.)')
    end_time = models.TimeField('Окончание')
    seats = models.PositiveIntegerField('Мест')
    customer_name = models.CharField('Имя', max_length=150)
    customer_email = models.EmailField('Email')
    comment = models.TextField('Комментарий', blank=True)

    status = models.CharField('Статус', max_length=20, choices=RESERVATION_STATUSES, default='NEW')

    public_code = models.CharField('Код билета', max_length=32, unique=True, editable=False)
    email_sent_at = models.DateTimeField('Отправлено на email', null=True, blank=True)

    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        """Мета-настройки модели или формы."""
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        indexes = [
            models.Index(fields=['date', 'start_time']),
            models.Index(fields=['table', 'date']),
        ]

    def __str__(self) -> str:
        """Возвращает человекочитаемое строковое представление объекта."""
        return f'{self.date} {self.start_time} {self.table}'

    def clean(self) -> None:
        """Валидирует состояние объекта и выбрасывает ошибки при нарушении правил."""
        if not self.table.is_active:
            raise ValidationError('Стол неактивен и не может быть забронирован.')
        if self.seats > self.table.capacity:
            raise ValidationError('Количество мест превышает вместимость стола.')

        settings = SiteSettings.get_solo()
        duration_choices = settings.slot_duration_choices or [60, 120, 180, 240]
        if self.duration_minutes not in duration_choices:
            raise ValidationError('Выбрана недоступная длительность.')

        window = get_working_window(self.date)
        if window is None:
            raise ValidationError('На выбранную дату бронирования не принимаются.')
        open_time, close_time = window
        end_time = compute_end_time(self.start_time, self.duration_minutes)
        if self.start_time < open_time or end_time > close_time:
            raise ValidationError('Бронирование выходит за пределы рабочего времени.')

        if not is_table_available(self.table, self.date, self.start_time, end_time, exclude_id=self.id):
            raise ValidationError('Стол уже занят в это время.')

        now = timezone.localtime()
        reservation_dt = timezone.make_aware(datetime.combine(self.date, self.start_time), now.tzinfo)
        min_notice = timedelta(minutes=settings.min_notice_minutes)
        if reservation_dt - now < min_notice:
            raise ValidationError('Слишком поздно для бронирования на это время.')

    def save(self, *args, **kwargs):
        """Сохраняет объект, предварительно выполняя вычисления и валидацию."""
        if not self.public_code:
            self.public_code = uuid.uuid4().hex[:12].upper()
        self.end_time = compute_end_time(self.start_time, self.duration_minutes)
        self.full_clean()
        super().save(*args, **kwargs)
