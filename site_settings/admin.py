from django.contrib import admin

from .models import SiteSettings, SpecialDay, WeeklySchedule


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Основное', {'fields': ('site_name', 'site_description', 'address', 'phone', 'logo')}),
        ('SEO', {'fields': ('meta_title', 'meta_description', 'og_image')}),
        ('Бронирования', {'fields': ('deposit_amount', 'currency', 'slot_duration_choices', 'min_notice_minutes')}),
        ('Telegram', {'fields': ('tg_enabled', 'tg_bot_token', 'tg_chat_id')}),
        ('Email', {'fields': ('from_email', 'reply_to_email')}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


@admin.register(WeeklySchedule)
class WeeklyScheduleAdmin(admin.ModelAdmin):
    list_display = ('day_of_week', 'is_open', 'open_time', 'close_time')
    list_editable = ('is_open', 'open_time', 'close_time')


@admin.register(SpecialDay)
class SpecialDayAdmin(admin.ModelAdmin):
    list_display = ('date', 'is_open', 'open_time', 'close_time', 'note')
    list_editable = ('is_open', 'open_time', 'close_time', 'note')
