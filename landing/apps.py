from django.apps import AppConfig


class LandingConfig(AppConfig):
    """Конфигурация приложения лендинга."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'landing'
    verbose_name = 'Лендинг'
