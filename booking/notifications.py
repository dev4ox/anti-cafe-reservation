import logging

from django.core.mail import EmailMessage

from site_settings.models import SiteSettings

logger = logging.getLogger(__name__)


def send_email_ticket(reservation, ticket_url) -> bool:
    """Отправляет письмо с билетом и сообщает об успехе."""
    settings = SiteSettings.get_solo()
    start_time = reservation.start_time.strftime('%H:%M')
    subject = f'Бронирование в {settings.site_name} на {reservation.date} {start_time}'
    deposit_line = ''
    if settings.deposit_required:
        deposit_line = f'Депозит: {settings.deposit_amount} {settings.currency}\n'

    body = (
        f'Дата: {reservation.date}\n'
        f'Время: {start_time}\n'
        f'Длительность: {reservation.duration_minutes} мин.\n'
        f'Стол: {reservation.table.name}\n'
        f'Мест: {reservation.seats}\n'
        f'{deposit_line}'
        f'Адрес: {settings.address}\n'
        f'Телефон: {settings.phone}\n'
        f'Код билета: {reservation.public_code}\n'
        f'Ссылка на билет: {ticket_url}\n'
    )

    reply_to = [settings.reply_to_email] if settings.reply_to_email else None
    email = EmailMessage(
        subject=subject,
        body=body,
        from_email=settings.from_email or None,
        to=[reservation.customer_email],
        reply_to=reply_to,
    )
    try:
        email.send(fail_silently=False)
    except Exception:
        logger.exception('Failed to send email ticket for reservation %s', reservation.id)
        return False
    return True
