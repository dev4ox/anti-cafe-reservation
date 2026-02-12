from django.apps import AppConfig


class BookingConfig(AppConfig):
    """Конфигурация приложения бронирований."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'booking'
    verbose_name = 'Бронирования'
