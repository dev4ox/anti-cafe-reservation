from datetime import datetime, timedelta
from typing import Iterable

from django.apps import apps
from django.db.models import Q
from django.utils import timezone

from site_settings.models import SiteSettings

from .constants import OCCUPYING_STATUSES
from .utils import compute_end_time, get_working_window


def is_table_available(table, date, start_time, end_time, exclude_id=None) -> bool:
    Reservation = apps.get_model('booking', 'Reservation')
    qs = Reservation.objects.filter(
        table=table,
        date=date,
        status__in=OCCUPYING_STATUSES,
    ).filter(
        Q(start_time__lt=end_time) & Q(end_time__gt=start_time)
    )
    if exclude_id:
        qs = qs.exclude(id=exclude_id)
    return not qs.exists()


def find_available_tables(date, start_time, end_time, seats) -> Iterable:
    Table = apps.get_model('booking', 'Table')
    tables = Table.objects.filter(is_active=True, capacity__gte=seats).order_by('capacity', 'name')
    return [table for table in tables if is_table_available(table, date, start_time, end_time)]


def find_available_start_times(date, duration_minutes, seats, step_minutes=30):
    window = get_working_window(date)
    if window is None:
        return []
    open_time, close_time = window

    settings = SiteSettings.get_solo()
    tz = timezone.get_current_timezone()
    open_dt = timezone.make_aware(datetime.combine(date, open_time), tz)
    close_dt = timezone.make_aware(datetime.combine(date, close_time), tz)
    start_dt = open_dt
    results = []

    # Учитываем минимальное время предупреждения для пользователя.
    min_notice_dt = timezone.localtime() + timedelta(minutes=settings.min_notice_minutes)
    if timezone.is_naive(start_dt):
        start_dt = timezone.make_aware(start_dt, timezone.get_current_timezone())
    if timezone.is_naive(min_notice_dt):
        min_notice_dt = timezone.make_aware(min_notice_dt, timezone.get_current_timezone())

    # Подбираем слоты с шагом step_minutes и проверяем пересечения по каждому столу.
    while start_dt + timedelta(minutes=duration_minutes) <= close_dt:
        if start_dt < min_notice_dt:
            start_dt += timedelta(minutes=step_minutes)
            continue
        start_time = start_dt.time()
        end_time = (start_dt + timedelta(minutes=duration_minutes)).time()
        if find_available_tables(date, start_time, end_time, seats):
            results.append(start_time)
        start_dt += timedelta(minutes=step_minutes)
    return results


def find_available_tables_for_date(date, duration_minutes, seats, step_minutes=30):
    window = get_working_window(date)
    if window is None:
        return []
    open_time, close_time = window

    settings = SiteSettings.get_solo()
    tz = timezone.get_current_timezone()
    open_dt = timezone.make_aware(datetime.combine(date, open_time), tz)
    close_dt = timezone.make_aware(datetime.combine(date, close_time), tz)
    start_dt = open_dt
    results = {}

    min_notice_dt = timezone.localtime() + timedelta(minutes=settings.min_notice_minutes)
    if timezone.is_naive(start_dt):
        start_dt = timezone.make_aware(start_dt, timezone.get_current_timezone())
    if timezone.is_naive(min_notice_dt):
        min_notice_dt = timezone.make_aware(min_notice_dt, timezone.get_current_timezone())

    while start_dt + timedelta(minutes=duration_minutes) <= close_dt:
        if start_dt < min_notice_dt:
            start_dt += timedelta(minutes=step_minutes)
            continue
        start_time = start_dt.time()
        end_time = (start_dt + timedelta(minutes=duration_minutes)).time()
        for table in find_available_tables(date, start_time, end_time, seats):
            results[table.id] = table
        start_dt += timedelta(minutes=step_minutes)
    return sorted(results.values(), key=lambda t: (t.capacity, t.name))


def find_available_start_times_for_table(date, duration_minutes, seats, table, step_minutes=30):
    window = get_working_window(date)
    if window is None:
        return []
    open_time, close_time = window

    settings = SiteSettings.get_solo()
    tz = timezone.get_current_timezone()
    open_dt = timezone.make_aware(datetime.combine(date, open_time), tz)
    close_dt = timezone.make_aware(datetime.combine(date, close_time), tz)
    start_dt = open_dt
    results = []

    min_notice_dt = timezone.localtime() + timedelta(minutes=settings.min_notice_minutes)
    if timezone.is_naive(start_dt):
        start_dt = timezone.make_aware(start_dt, timezone.get_current_timezone())
    if timezone.is_naive(min_notice_dt):
        min_notice_dt = timezone.make_aware(min_notice_dt, timezone.get_current_timezone())

    while start_dt + timedelta(minutes=duration_minutes) <= close_dt:
        if start_dt < min_notice_dt:
            start_dt += timedelta(minutes=step_minutes)
            continue
        start_time = start_dt.time()
        end_time = (start_dt + timedelta(minutes=duration_minutes)).time()
        if seats <= table.capacity and is_table_available(table, date, start_time, end_time):
            results.append(start_time)
        start_dt += timedelta(minutes=step_minutes)
    return results
