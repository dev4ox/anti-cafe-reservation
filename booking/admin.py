from django.contrib import admin

from .models import Reservation, Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'is_active')
    list_editable = ('capacity', 'is_active')
    search_fields = ('name',)


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('date', 'start_time', 'table', 'seats', 'status', 'customer_name')
    list_filter = ('status', 'date')
    search_fields = ('customer_name', 'customer_email', 'public_code')
