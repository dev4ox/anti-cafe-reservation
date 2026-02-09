from django import forms
from django.db.models import Max

from site_settings.models import SiteSettings

from .models import Reservation, Table
from .services import find_available_tables
from .utils import compute_end_time


class BookingAvailabilityForm(forms.Form):
    date = forms.DateField(label='Дата', widget=forms.DateInput(attrs={'type': 'date'}))
    duration_minutes = forms.ChoiceField(label='Длительность (мин.)')
    seats = forms.IntegerField(label='Мест')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings = SiteSettings.get_solo()
        duration_choices = settings.slot_duration_choices or [60, 120, 180, 240]
        choices = [(value, f'{value} мин.') for value in duration_choices]
        self.fields['duration_minutes'].choices = choices
        max_capacity = Table.objects.filter(is_active=True).aggregate(max_capacity=Max('capacity'))
        max_value = max_capacity.get('max_capacity') or 1
        self.fields['seats'].min_value = 1
        self.fields['seats'].max_value = max_value
        self.fields['seats'].widget.attrs['min'] = 1
        self.fields['seats'].widget.attrs['max'] = max_value

    def clean_duration_minutes(self):
        duration = int(self.cleaned_data['duration_minutes'])
        settings = SiteSettings.get_solo()
        if settings.slot_duration_choices and duration not in settings.slot_duration_choices:
            raise forms.ValidationError('Выберите длительность из доступных.')
        return duration


class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'table',
            'date',
            'start_time',
            'duration_minutes',
            'seats',
            'customer_name',
            'customer_email',
            'comment',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        date = kwargs.pop('date', None)
        start_time = kwargs.pop('start_time', None)
        duration_minutes = kwargs.pop('duration_minutes', None)
        seats = kwargs.pop('seats', None)
        available_tables = kwargs.pop('available_tables', None)
        table_id = kwargs.pop('table_id', None)
        lock_fields = kwargs.pop('lock_fields', False)
        super().__init__(*args, **kwargs)

        settings = SiteSettings.get_solo()
        duration_choices = settings.slot_duration_choices or [60, 120, 180, 240]
        self.fields['duration_minutes'].widget = forms.Select(
            choices=[(value, f'{value} мин.') for value in duration_choices]
        )

        if date and start_time and duration_minutes and seats:
            end_time = compute_end_time(start_time, duration_minutes)
            if available_tables is None:
                available_tables = find_available_tables(date, start_time, end_time, seats)
            self.fields['table'].queryset = Table.objects.filter(
                id__in=[t.id for t in available_tables]
            )

        if table_id:
            try:
                self.initial['table'] = int(table_id)
            except (TypeError, ValueError):
                pass

        if lock_fields:
            for field_name in ['date', 'start_time', 'duration_minutes', 'seats', 'table']:
                if field_name in self.fields:
                    self.fields[field_name].widget = forms.HiddenInput()
