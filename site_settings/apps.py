from django.apps import AppConfig


class SiteSettingsConfig(AppConfig):
    """Конфигурация приложения настроек сайта."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'site_settings'
    verbose_name = 'Настройки сайта'
