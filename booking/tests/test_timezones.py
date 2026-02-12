from datetime import time, timedelta

from django.test import TestCase
from django.utils import timezone

from booking.models import Reservation, Table
from booking.utils import compute_end_time
from booking.services import find_available_start_times
from site_settings.models import SiteSettings, WeeklySchedule


class BookingTimezoneTests(TestCase):
    """Тесты корректности работы с часовыми поясами."""
    def setUp(self):
        """Готовит тестовые данные для сценариев."""
        settings = SiteSettings.get_solo()
        settings.slot_duration_choices = [60, 120, 180]
        settings.min_notice_minutes = 0
        settings.save()

        WeeklySchedule.objects.all().delete()
        WeeklySchedule.objects.create(
            day_of_week=timezone.localdate().weekday(),
            is_open=True,
            open_time=time(10, 0),
            close_time=time(22, 0),
        )
        WeeklySchedule.objects.create(
            day_of_week=(timezone.localdate() + timedelta(days=1)).weekday(),
            is_open=True,
            open_time=time(10, 0),
            close_time=time(22, 0),
        )

        self.table = Table.objects.create(name="T1", capacity=4, is_active=True)

    def test_find_available_start_times_aware(self):
        """Проверяет сценарий: find available start times aware."""
        date = timezone.localdate()
        times = find_available_start_times(date, 60, 2)
        self.assertTrue(times)

    def test_reservation_clean_aware(self):
        """Проверяет сценарий: reservation clean aware."""
        date = timezone.localdate() + timedelta(days=1)
        reservation = Reservation(
            table=self.table,
            date=date,
            start_time=time(12, 0),
            duration_minutes=60,
            end_time=compute_end_time(time(12, 0), 60),
            seats=2,
            customer_name="Test",
            customer_email="test@example.com",
        )
        reservation.full_clean()
