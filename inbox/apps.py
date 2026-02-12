from django.apps import AppConfig


class InboxConfig(AppConfig):
    """Конфигурация приложения входящих сообщений."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inbox'
    verbose_name = 'Сообщения'
