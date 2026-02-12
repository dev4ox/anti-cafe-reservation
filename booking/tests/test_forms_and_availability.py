from datetime import time, timedelta

from django.test import TestCase
from django.utils import timezone

from booking.forms import BookingAvailabilityForm, ReservationForm
from booking.models import Reservation, Table
from booking.services import find_available_start_times
from booking.utils import compute_end_time
from site_settings.models import SiteSettings, WeeklySchedule


class BookingFormsAndAvailabilityTests(TestCase):
    """Тесты форм и доступности слотов."""
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

        self.date = tomorrow
        self.table_small = Table.objects.create(name="T1", capacity=2, is_active=True)
        self.table_large = Table.objects.create(name="T2", capacity=4, is_active=True)

    def test_booking_availability_form_uses_settings_choices(self):
        """Проверяет сценарий: booking availability form uses settings choices."""
        form = BookingAvailabilityForm()
        choices = [int(value) for value, _ in form.fields['duration_minutes'].choices]
        self.assertEqual(choices, [60, 120])

    def test_reservation_form_limits_tables_by_availability(self):
        """Проверяет сценарий: reservation form limits tables by availability."""
        Reservation.objects.create(
            table=self.table_large,
            date=self.date,
            start_time=time(12, 0),
            duration_minutes=120,
            end_time=compute_end_time(time(12, 0), 120),
            seats=2,
            customer_name="Test",
            customer_email="test@example.com",
        )
        form = ReservationForm(
            date=self.date,
            start_time=time(12, 0),
            duration_minutes=60,
            seats=2,
        )
        table_ids = list(form.fields['table'].queryset.values_list('id', flat=True))
        self.assertEqual(table_ids, [self.table_small.id])

    def test_find_available_start_times_respects_existing_reservation(self):
        """Проверяет сценарий: find available start times respects existing reservation."""
        Reservation.objects.create(
            table=self.table_large,
            date=self.date,
            start_time=time(12, 0),
            duration_minutes=120,
            end_time=compute_end_time(time(12, 0), 120),
            seats=2,
            customer_name="Test",
            customer_email="test@example.com",
        )
        times = find_available_start_times(self.date, 60, 3, step_minutes=60)
        self.assertIn(time(10, 0), times)
        self.assertNotIn(time(13, 0), times)
