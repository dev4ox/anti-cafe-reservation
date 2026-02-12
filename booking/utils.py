from datetime import datetime, timedelta

from django.utils import timezone

from site_settings.models import SpecialDay, WeeklySchedule


def get_working_window(date):
    """Возвращает рабочее окно на дату с учетом исключений."""
    special = SpecialDay.objects.filter(date=date).first()
    if special:
        if not special.is_open:
            return None
        if special.open_time is None or special.close_time is None:
            return None
        return special.open_time, special.close_time

    weekly = WeeklySchedule.objects.filter(day_of_week=date.weekday()).first()
    if not weekly or not weekly.is_open:
        return None
    if weekly.open_time is None or weekly.close_time is None:
        return None
    return weekly.open_time, weekly.close_time


def compute_end_time(start_time, duration_minutes):
    """Вычисляет время окончания по началу и длительности."""
    start_dt = datetime.combine(timezone.localdate(), start_time)
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    return end_dt.time()
