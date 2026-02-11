from datetime import time, timedelta
from unittest.mock import patch

from django.contrib.messages import constants as message_constants
from django.test import TestCase
from django.utils import timezone

from booking.models import Reservation, Table
from site_settings.models import SiteSettings, WeeklySchedule


class BookingViewsTests(TestCase):
    def setUp(self):
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
        self.table = Table.objects.create(name="T1", capacity=4, is_active=True)

    def test_booking_index_shows_available_tables(self):
        response = self.client.get(
            '/booking/',
            {
                'date': self.date.isoformat(),
                'duration_minutes': 60,
                'seats': 2,
            },
        )
        self.assertEqual(response.status_code, 200)
        available_tables = response.context['available_tables']
        self.assertEqual([t.id for t in available_tables], [self.table.id])

    def test_booking_create_creates_reservation_and_redirects(self):
        response = self.client.post(
            '/booking/new/',
            {
                'table': self.table.id,
                'date': self.date.isoformat(),
                'start_time': '12:00',
                'duration_minutes': 60,
                'seats': 2,
                'customer_name': 'Test',
                'customer_email': 'test@example.com',
                'comment': '',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Reservation.objects.exists())
        reservation = Reservation.objects.first()
        self.assertIsNotNone(reservation.email_sent_at)

    def test_booking_create_email_failure_warns_and_skips_sent_at(self):
        with patch('booking.views.send_email_ticket', return_value=False):
            response = self.client.post(
                '/booking/new/',
                {
                    'table': self.table.id,
                    'date': self.date.isoformat(),
                    'start_time': '12:00',
                    'duration_minutes': 60,
                    'seats': 2,
                    'customer_name': 'Test',
                    'customer_email': 'test@example.com',
                    'comment': '',
                },
                follow=True,
            )
        reservation = Reservation.objects.first()
        self.assertIsNone(reservation.email_sent_at)
        messages = list(response.context['messages'])
        self.assertTrue(any(msg.level == message_constants.WARNING for msg in messages))
