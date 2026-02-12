from django.apps import AppConfig


class StaffConfig(AppConfig):
    """Конфигурация приложения панели персонала."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'staff'
    verbose_name = 'Staff'
