from datetime import time, timedelta

import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from booking.constants import (
    STATUS_CANCELLED,
    STATUS_COMPLETED,
    STATUS_CONFIRMED,
    STATUS_NEW,
    STATUS_NO_SHOW,
)
from booking.models import Reservation, Table
from booking.services import is_table_available
from booking.utils import compute_end_time, get_working_window
from catalog.models import BoardGame, Product
from inbox.models import ContactMessage
from site_settings.models import SiteSettings, SpecialDay, WeeklySchedule


class Command(BaseCommand):
    help = "Seed demo data for local development."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing demo data before seeding.",
        )
        parser.add_argument(
            "--big",
            action="store_true",
            help="Create a larger dataset (more reservations and messages).",
        )
        parser.add_argument(
            "--days",
            type=int,
            default=7,
            help="Number of future days to create reservations for.",
        )
        parser.add_argument(
            "--only",
            type=str,
            default="all",
            help="Seed only a specific section: all, settings, schedule, tables, games, products, messages, reservations, special-days.",
        )
        parser.add_argument(
            "--with-special-days",
            action="store_true",
            help="Create a few special days in the schedule.",
        )
        parser.add_argument(
            "--realistic",
            action="store_true",
            help="Use pseudo-random realistic data (deterministic seed).",
        )
        parser.add_argument(
            "--append-reservations",
            action="store_true",
            help="Append reservations even if they already exist.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            Reservation.objects.all().delete()
            Table.objects.all().delete()
            BoardGame.objects.all().delete()
            Product.objects.all().delete()
            ContactMessage.objects.all().delete()
            WeeklySchedule.objects.all().delete()
            SpecialDay.objects.all().delete()
            SiteSettings.objects.all().delete()

        only = options["only"].strip().lower()

        def wants(section):
            return only == "all" or only == section

        settings = SiteSettings.get_solo()
        if wants("settings"):
            settings.site_name = settings.site_name or "Антикафе"
            settings.site_description = settings.site_description or "Уютное пространство для игр и встреч."
            settings.address = settings.address or "Москва, ул. Примерная, 1"
            settings.phone = settings.phone or "+7 (999) 123-45-67"
            settings.slot_duration_choices = settings.slot_duration_choices or [60, 120, 180, 240]
            settings.save()

        if wants("schedule") and not WeeklySchedule.objects.exists():
            for day in range(7):
                WeeklySchedule.objects.create(
                    day_of_week=day,
                    is_open=True,
                    open_time=time(10, 0),
                    close_time=time(23, 0),
                )

        if wants("special-days") and options["with_special_days"] and not SpecialDay.objects.exists():
            today = timezone.localdate()
            SpecialDay.objects.create(
                date=today + timedelta(days=2),
                is_open=True,
                open_time=time(12, 0),
                close_time=time(20, 0),
                note="Укороченный день",
            )
            SpecialDay.objects.create(
                date=today + timedelta(days=4),
                is_open=False,
                note="Закрыто на мероприятие",
            )

        if wants("tables") and not Table.objects.exists():
            Table.objects.create(name="Стол 1", capacity=2, is_active=True)
            Table.objects.create(name="Стол 2", capacity=4, is_active=True)
            Table.objects.create(name="Стол 3", capacity=6, is_active=True)
            Table.objects.create(name="VIP", capacity=8, is_active=True, location_note="У окна")

        if wants("games") and not BoardGame.objects.exists():
            BoardGame.objects.create(
                title="Alias",
                description="Командная игра на объяснение слов.",
                players_min=4,
                players_max=12,
                play_time_min=45,
                age=12,
            )
            BoardGame.objects.create(
                title="Каркассон",
                description="Стратегия про средневековые города.",
                players_min=2,
                players_max=5,
                play_time_min=40,
                age=8,
            )
            BoardGame.objects.create(
                title="Имаджинариум",
                description="Ассоциации и красивые иллюстрации.",
                players_min=3,
                players_max=7,
                play_time_min=50,
                age=12,
            )

        if wants("products") and not Product.objects.exists():
            Product.objects.create(title="Капучино", price=220, description="Классический капучино.")
            Product.objects.create(title="Матча латте", price=260, description="Мягкий вкус матча.")
            Product.objects.create(title="Чизкейк", price=290, description="Нежный десерт.")

        if wants("messages") and not ContactMessage.objects.exists():
            ContactMessage.objects.create(
                name="Алина",
                phone="+7 (900) 555-44-33",
                message="Можно забронировать на пятницу?",
            )
            if options["big"]:
                if options["realistic"]:
                    ContactMessage.objects.create(
                        name="Олег Соловьев",
                        phone="+7 (911) 555-22-11",
                        message="Хотим корпоратив на 12 человек.",
                    )
                    ContactMessage.objects.create(
                        name="Светлана Кравцова",
                        phone="+7 (926) 123-45-67",
                        message="Есть ли свободные столы сегодня после 19:00?",
                    )
                    ContactMessage.objects.create(
                        name="Денис Павлов",
                        phone="+7 (905) 777-88-99",
                        message="Нужна бронь на 4 человека завтра вечером.",
                    )
                else:
                    ContactMessage.objects.create(
                        name="Олег",
                        phone="+7 (911) 555-22-11",
                        message="Хотим корпоратив на 12 человек.",
                    )
                    ContactMessage.objects.create(
                        name="Светлана",
                        phone="+7 (926) 123-45-67",
                        message="Есть ли свободные столы сегодня после 19:00?",
                    )

        if wants("reservations") and (options["append_reservations"] or not Reservation.objects.exists()):
            if not WeeklySchedule.objects.exists():
                for day in range(7):
                    WeeklySchedule.objects.create(
                        day_of_week=day,
                        is_open=True,
                        open_time=time(10, 0),
                        close_time=time(23, 0),
                    )
            tables = list(Table.objects.all().order_by("capacity"))
            if tables:
                self._seed_reservations(
                    tables,
                    options["days"],
                    options["big"],
                    options["realistic"],
                )

        self.stdout.write(self.style.SUCCESS("Demo data seeded."))

    def _seed_reservations(self, tables, days, big, realistic):
        durations = [60, 120, 180]
        statuses = [STATUS_NEW, STATUS_CONFIRMED, STATUS_COMPLETED, STATUS_CANCELLED, STATUS_NO_SHOW]
        start_times = [time(11, 0), time(13, 0), time(15, 0), time(18, 0), time(20, 0)]
        rng = random.Random(42)
        names = [
            "Иван", "Мария", "Алексей", "Ольга", "Дмитрий", "Анна",
            "Сергей", "Елена", "Павел", "Наталья", "Кирилл", "Дарья",
        ]
        last_names = [
            "Иванов", "Петров", "Сидоров", "Смирнов", "Кузнецов", "Попова",
            "Васильев", "Морозова", "Новиков", "Федорова", "Орлов", "Мельникова",
        ]
        today = timezone.localdate()
        count_per_day = 3 if not big else 6

        for offset in range(1, max(1, days) + 1):
            target_date = today + timedelta(days=offset)
            created = 0
            window = get_working_window(target_date)
            if window is None:
                continue
            open_time, close_time = window
            times_iter = start_times[:]
            if realistic:
                rng.shuffle(times_iter)
            for start in times_iter:
                if created >= count_per_day:
                    break
                table_iter = tables[:]
                if realistic:
                    rng.shuffle(table_iter)
                for table in table_iter:
                    duration = rng.choice(durations) if realistic else durations[created % len(durations)]
                    end_time = compute_end_time(start, duration)
                    if start < open_time or end_time > close_time:
                        continue
                    if is_table_available(table, target_date, start, end_time):
                        status = rng.choice(statuses) if realistic else statuses[(offset + created) % len(statuses)]
                        if realistic:
                            first = rng.choice(names)
                            last = rng.choice(last_names)
                            customer_name = f"{first} {last}"
                            email = f"{first.lower()}.{last.lower()}@example.com"
                        else:
                            customer_name = f"Гость {offset}-{created + 1}"
                            email = f"guest{offset}{created + 1}@example.com"
                        Reservation.objects.create(
                            table=table,
                            date=target_date,
                            start_time=start,
                            duration_minutes=duration,
                            seats=min(table.capacity, 2 + created % max(1, table.capacity)),
                            customer_name=customer_name,
                            customer_email=email,
                            status=status,
                        )
                        created += 1
                        break
