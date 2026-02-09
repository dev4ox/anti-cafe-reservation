from datetime import datetime

from django.contrib import messages
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from integrations.telegram import send_telegram_message

from .forms import BookingAvailabilityForm, ReservationForm
from .models import Reservation
from .notifications import send_email_ticket
from .services import (
    find_available_start_times_for_table,
    find_available_tables,
    find_available_tables_for_date,
)
from .utils import compute_end_time


def booking_index(request):
    availability_form = BookingAvailabilityForm(request.GET or None)
    reservation_form = None
    available_times = []
    available_tables = []
    selected_time = None
    selected_table = None
    selected_table_obj = None

    if availability_form.is_valid():
        date = availability_form.cleaned_data['date']
        duration = availability_form.cleaned_data['duration_minutes']
        seats = availability_form.cleaned_data['seats']
        available_tables = find_available_tables_for_date(date, duration, seats)
        selected_time_raw = request.GET.get('start_time')
        if selected_time_raw:
            try:
                selected_time = datetime.strptime(selected_time_raw, '%H:%M').time()
            except ValueError:
                selected_time = None
        selected_table_raw = request.GET.get('table')
        if selected_table_raw:
            try:
                selected_table = int(selected_table_raw)
            except ValueError:
                selected_table = None
        if selected_table is not None:
            selected_table_obj = next((t for t in available_tables if t.id == selected_table), None)
            selected_table = selected_table_obj.id if selected_table_obj else None
        if selected_table_obj:
            available_times = find_available_start_times_for_table(
                date,
                duration,
                seats,
                selected_table_obj,
            )
        if selected_table_obj and selected_time:
            if selected_time not in available_times:
                selected_time = None
        if selected_table_obj and selected_time:
            reservation_form = ReservationForm(
                initial={
                    'date': date,
                    'duration_minutes': duration,
                    'seats': seats,
                    'start_time': selected_time,
                    'table': selected_table,
                },
                date=date,
                start_time=selected_time,
                duration_minutes=duration,
                seats=seats,
                available_tables=[selected_table_obj],
                table_id=selected_table,
                lock_fields=True,
            )
        elif selected_table_obj:
            reservation_form = ReservationForm(
                initial={'date': date, 'duration_minutes': duration, 'seats': seats},
                date=date,
                duration_minutes=duration,
                seats=seats,
                available_tables=[selected_table_obj],
                table_id=selected_table,
            )
        else:
            reservation_form = ReservationForm(
                initial={'date': date, 'duration_minutes': duration, 'seats': seats},
                date=date,
                duration_minutes=duration,
                seats=seats,
            )

    availability_data = {}
    if availability_form.is_valid():
        availability_data = availability_form.cleaned_data

    context = {
        'availability_form': availability_form,
        'reservation_form': reservation_form,
        'available_times': available_times,
        'available_tables': available_tables,
        'selected_time': selected_time,
        'selected_table': selected_table,
        'selected_table_obj': selected_table_obj,
        'availability_data': availability_data,
    }
    return render(request, 'booking/index.html', context)


def booking_create(request):
    if request.method != 'POST':
        return redirect('booking:index')

    form = ReservationForm(request.POST)
    if form.is_valid():
        reservation = form.save()
        ticket_url = request.build_absolute_uri(
            reverse('booking:ticket', kwargs={'public_code': reservation.public_code})
        )
        send_email_ticket(reservation, ticket_url)
        reservation.email_sent_at = timezone.now()
        reservation.save(update_fields=['email_sent_at'])

        start_time = reservation.start_time.strftime('%H:%M')
        send_telegram_message(
            f'Новая бронь: {reservation.date} {start_time}, '
            f'{reservation.duration_minutes} мин., {reservation.table.name}, '
            f'мест: {reservation.seats}, {reservation.customer_name}, '
            f'email: {reservation.customer_email}, код: {reservation.public_code}'
        )
        return redirect('booking:success')

    messages.error(request, 'Проверьте форму бронирования.')
    availability_form = BookingAvailabilityForm(request.POST or None)
    available_tables = []
    available_times = []
    selected_time = None
    selected_table = None
    selected_table_obj = None
    availability_data = {}
    if availability_form.is_valid():
        availability_data = availability_form.cleaned_data
        date = availability_data['date']
        duration = availability_data['duration_minutes']
        seats = availability_data['seats']
        available_tables = find_available_tables_for_date(date, duration, seats)
        selected_table = request.POST.get('table')
        try:
            selected_table = int(selected_table) if selected_table else None
        except ValueError:
            selected_table = None
        if selected_table is not None:
            selected_table_obj = next((t for t in available_tables if t.id == selected_table), None)
            selected_table = selected_table_obj.id if selected_table_obj else None
        if selected_table_obj:
            available_times = find_available_start_times_for_table(date, duration, seats, selected_table_obj)
        selected_time = request.POST.get('start_time')
        if selected_time:
            try:
                selected_time = datetime.strptime(selected_time, '%H:%M').time()
            except ValueError:
                selected_time = None
    return render(
        request,
        'booking/index.html',
        {
            'availability_form': availability_form,
            'reservation_form': form,
            'available_times': available_times,
            'available_tables': available_tables,
            'selected_time': selected_time,
            'selected_table': selected_table,
            'selected_table_obj': selected_table_obj,
            'availability_data': availability_data,
        },
    )


def booking_success(request):
    return render(request, 'booking/success.html')


def booking_ticket(request, public_code):
    reservation = get_object_or_404(Reservation, public_code=public_code)
    return render(request, 'booking/ticket.html', {'reservation': reservation})
