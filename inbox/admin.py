from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Админ-конфигурация для сообщений."""
    list_display = ('name', 'phone', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'phone', 'message')
