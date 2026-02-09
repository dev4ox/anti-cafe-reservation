import json
from urllib import request

from site_settings.models import SiteSettings


def send_telegram_message(text: str) -> None:
    settings = SiteSettings.get_solo()
    if not settings.tg_enabled:
        return
    if not settings.tg_bot_token or not settings.tg_chat_id:
        return

    url = f'https://api.telegram.org/bot{settings.tg_bot_token}/sendMessage'
    payload = json.dumps({'chat_id': settings.tg_chat_id, 'text': text}).encode('utf-8')

    # Важно: это простой вызов без повторов и очередей, чтобы MVP оставался легким.
    req = request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
    try:
        request.urlopen(req, timeout=5)
    except Exception:
        # В MVP игнорируем ошибки, чтобы не ломать основной поток бронирования.
        return
