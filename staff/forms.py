from django import forms

from booking.models import Reservation, Table
from catalog.models import BoardGame, Product
from site_settings.models import SiteSettings, SpecialDay, WeeklySchedule


class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['name', 'capacity', 'is_active', 'location_note']


class ReservationStatusForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['status']


class BoardGameForm(forms.ModelForm):
    class Meta:
        model = BoardGame
        fields = [
            'title',
            'description',
            'players_min',
            'players_max',
            'play_time_min',
            'age',
            'image',
            'is_available',
        ]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'price', 'description', 'image', 'is_available']


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            'site_name',
            'site_description',
            'address',
            'phone',
            'logo',
            'meta_title',
            'meta_description',
            'og_image',
            'deposit_amount',
            'currency',
            'slot_duration_choices',
            'min_notice_minutes',
            'tg_enabled',
            'tg_bot_token',
            'tg_chat_id',
            'from_email',
            'reply_to_email',
        ]


class WeeklyScheduleForm(forms.ModelForm):
    class Meta:
        model = WeeklySchedule
        fields = ['day_of_week', 'is_open', 'open_time', 'close_time']


class SpecialDayForm(forms.ModelForm):
    class Meta:
        model = SpecialDay
        fields = ['date', 'is_open', 'open_time', 'close_time', 'note']
