from django.core.mail import send_mail

from site_settings.models import SiteSettings


def send_email_ticket(reservation, ticket_url):
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

    send_mail(
        subject=subject,
        message=body,
        from_email=settings.from_email or None,
        recipient_list=[reservation.customer_email],
        fail_silently=False,
        reply_to=[settings.reply_to_email] if settings.reply_to_email else None,
    )
