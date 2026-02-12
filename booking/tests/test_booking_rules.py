from datetime import time, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from booking.models import Reservation, Table
from booking.utils import compute_end_time
from site_settings.models import SiteSettings, WeeklySchedule


class BookingRulesTests(TestCase):
    """Тесты бизнес-правил бронирования."""
    def setUp(self):
        """Готовит тестовые данные для сценариев."""
        settings = SiteSettings.get_solo()
        settings.slot_duration_choices = [60, 120]
        settings.min_notice_minutes = 0
        settings.save()

        WeeklySchedule.objects.all().delete()
        today = timezone.localdate()
        tomorrow = today + timedelta(days=1)
        WeeklySchedule.objects.create(
            day_of_week=today.weekday(),
            is_open=True,
            open_time=time(10, 0),
            close_time=time(22, 0),
        )
        WeeklySchedule.objects.create(
            day_of_week=tomorrow.weekday(),
            is_open=True,
            open_time=time(10, 0),
            close_time=time(22, 0),
        )

        self.table = Table.objects.create(name="T1", capacity=4, is_active=True)

    def test_reservation_rejects_outside_working_hours(self):
        """Проверяет сценарий: reservation rejects outside working hours."""
        date = timezone.localdate() + timedelta(days=1)
        reservation = Reservation(
            table=self.table,
            date=date,
            start_time=time(9, 0),
            duration_minutes=60,
            end_time=compute_end_time(time(9, 0), 60),
            seats=2,
            customer_name="Test",
            customer_email="test@example.com",
        )
        with self.assertRaises(ValidationError):
            reservation.full_clean()

    def test_reservation_rejects_seats_over_capacity(self):
        """Проверяет сценарий: reservation rejects seats over capacity."""
        date = timezone.localdate() + timedelta(days=1)
        reservation = Reservation(
            table=self.table,
            date=date,
            start_time=time(12, 0),
            duration_minutes=60,
            end_time=compute_end_time(time(12, 0), 60),
            seats=5,
            customer_name="Test",
            customer_email="test@example.com",
        )
        with self.assertRaises(ValidationError):
            reservation.full_clean()

    def test_reservation_overlap_rejected(self):
        """Проверяет сценарий: reservation overlap rejected."""
        date = timezone.localdate() + timedelta(days=1)
        Reservation.objects.create(
            table=self.table,
            date=date,
            start_time=time(12, 0),
            duration_minutes=120,
            end_time=compute_end_time(time(12, 0), 120),
            seats=2,
            customer_name="Test",
            customer_email="test@example.com",
        )
        reservation = Reservation(
            table=self.table,
            date=date,
            start_time=time(13, 0),
            duration_minutes=60,
            end_time=compute_end_time(time(13, 0), 60),
            seats=2,
            customer_name="Test 2",
            customer_email="test2@example.com",
        )
        with self.assertRaises(ValidationError):
            reservation.full_clean()

    def test_reservation_respects_min_notice(self):
        """Проверяет сценарий: reservation respects min notice."""
        settings = SiteSettings.get_solo()
        settings.min_notice_minutes = 120
        settings.save()

        date = timezone.localdate()
        soon_time = (timezone.localtime() + timedelta(minutes=30)).time()
        reservation = Reservation(
            table=self.table,
            date=date,
            start_time=soon_time,
            duration_minutes=60,
            end_time=compute_end_time(soon_time, 60),
            seats=2,
            customer_name="Test",
            customer_email="test@example.com",
        )
        with self.assertRaises(ValidationError):
            reservation.full_clean()
