from django.core.exceptions import ValidationError
from django.db import models


class SiteSettings(models.Model):
    site_name = models.CharField('Название сайта', max_length=200)
    site_description = models.TextField('Описание сайта')
    address = models.CharField('Адрес', max_length=255)
    phone = models.CharField('Телефон', max_length=50)
    logo = models.ImageField('Логотип', upload_to='logos/', blank=True)
    meta_title = models.CharField('Meta title', max_length=255, blank=True)
    meta_description = models.CharField('Meta description', max_length=255, blank=True)
    og_image = models.ImageField('OG image', upload_to='og/', blank=True)

    deposit_amount = models.DecimalField(
        'Депозит',
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    currency = models.CharField('Валюта', max_length=10, default='EUR')
    slot_duration_choices = models.JSONField(
        'Длительности слотов (мин.)',
        default=list,
        blank=True,
    )
    min_notice_minutes = models.PositiveIntegerField(
        'Минимальное время предупреждения (мин.)',
        default=30,
    )

    tg_enabled = models.BooleanField('Telegram включен', default=False)
    tg_bot_token = models.CharField('Telegram bot token', max_length=255, blank=True)
    tg_chat_id = models.CharField('Telegram chat id', max_length=255, blank=True)

    from_email = models.EmailField('Email отправителя', blank=True)
    reply_to_email = models.EmailField('Email для ответа', blank=True)

    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Настройки сайта'
        verbose_name_plural = 'Настройки сайта'

    def __str__(self) -> str:
        return 'Настройки сайта'

    @property
    def deposit_required(self) -> bool:
        return self.deposit_amount > 0

    @classmethod
    def get_solo(cls) -> "SiteSettings":
        settings = cls.objects.first()
        if settings:
            return settings
        return cls.objects.create(
            site_name='Антикафе',
            site_description='Уютное пространство для встреч и игр.',
            address='',
            phone='',
            slot_duration_choices=[60, 120, 180, 240],
        )


class WeeklySchedule(models.Model):
    day_of_week = models.IntegerField(
        'День недели',
        unique=True,
        help_text='0=Понедельник ... 6=Воскресенье',
    )
    is_open = models.BooleanField('Открыто', default=True)
    open_time = models.TimeField('Открытие', null=True, blank=True)
    close_time = models.TimeField('Закрытие', null=True, blank=True)

    class Meta:
        verbose_name = 'График по неделе'
        verbose_name_plural = 'График по неделе'
        ordering = ['day_of_week']

    def __str__(self) -> str:
        return f'День {self.day_of_week}'

    def clean(self) -> None:
        if self.is_open and (self.open_time is None or self.close_time is None):
            raise ValidationError('Для открытого дня нужно указать время работы.')
        if self.is_open and self.open_time and self.close_time and self.open_time >= self.close_time:
            raise ValidationError('Время открытия должно быть раньше времени закрытия.')


class SpecialDay(models.Model):
    date = models.DateField('Дата', unique=True)
    is_open = models.BooleanField('Открыто', default=True)
    open_time = models.TimeField('Открытие', null=True, blank=True)
    close_time = models.TimeField('Закрытие', null=True, blank=True)
    note = models.CharField('Примечание', max_length=255, blank=True)

    class Meta:
        verbose_name = 'Особый день'
        verbose_name_plural = 'Особые дни'
        ordering = ['date']

    def __str__(self) -> str:
        return self.date.isoformat()

    def clean(self) -> None:
        if self.is_open and (self.open_time is None or self.close_time is None):
            raise ValidationError('Для открытого дня нужно указать время работы.')
        if self.is_open and self.open_time and self.close_time and self.open_time >= self.close_time:
            raise ValidationError('Время открытия должно быть раньше времени закрытия.')
