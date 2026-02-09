from datetime import date as date_cls

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from booking.constants import RESERVATION_STATUSES
from booking.forms import ReservationForm
from booking.models import Reservation, Table
from catalog.models import BoardGame, Product
from inbox.models import ContactMessage
from integrations.telegram import send_telegram_message
from site_settings.models import SiteSettings, SpecialDay, WeeklySchedule

from .forms import (
    BoardGameForm,
    ProductForm,
    ReservationStatusForm,
    SiteSettingsForm,
    SpecialDayForm,
    TableForm,
    WeeklyScheduleForm,
)


def staff_required(view):
    return login_required(user_passes_test(lambda u: u.is_staff)(view))


@staff_required
def dashboard(request):
    today = date_cls.today()
    reservations = Reservation.objects.filter(date=today).order_by('start_time')
    return render(request, 'staff/dashboard.html', {'reservations': reservations, 'today': today})


@staff_required
def reservations_list(request):
    selected_date = request.GET.get('date') or date_cls.today().isoformat()
    status = request.GET.get('status')
    reservations = Reservation.objects.filter(date=selected_date)
    if status:
        reservations = reservations.filter(status=status)
    reservations = reservations.order_by('start_time')
    return render(
        request,
        'staff/reservations_list.html',
        {
            'reservations': reservations,
            'selected_date': selected_date,
            'status_choices': RESERVATION_STATUSES,
        },
    )


@staff_required
def reservation_status(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if request.method == 'POST':
        form = ReservationStatusForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            send_telegram_message(
                f'Статус брони изменен: {reservation.public_code} -> {reservation.get_status_display()}'
            )
            messages.success(request, 'Статус обновлен.')
    return redirect('staff:reservations')


@staff_required
def table_list(request):
    tables = Table.objects.all().order_by('name')
    form = TableForm()
    if request.method == 'POST':
        form = TableForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Стол добавлен.')
            return redirect('staff:tables')
    return render(request, 'staff/table_list.html', {'tables': tables, 'form': form})


@staff_required
def table_edit(request, table_id):
    table = get_object_or_404(Table, id=table_id)
    form = TableForm(request.POST or None, instance=table)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Стол обновлен.')
        return redirect('staff:tables')
    return render(request, 'staff/table_edit.html', {'form': form, 'table': table})


@staff_required
def messages_list(request):
    messages_list = ContactMessage.objects.all()
    return render(request, 'staff/messages_list.html', {'messages_list': messages_list})


@staff_required
def games_list(request):
    games = BoardGame.objects.all().order_by('title')
    form = BoardGameForm()
    if request.method == 'POST':
        form = BoardGameForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Игра добавлена.')
            return redirect('staff:games')
    return render(request, 'staff/games_list.html', {'games': games, 'form': form})


@staff_required
def game_edit(request, game_id):
    game = get_object_or_404(BoardGame, id=game_id)
    form = BoardGameForm(request.POST or None, request.FILES or None, instance=game)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Игра обновлена.')
        return redirect('staff:games')
    return render(request, 'staff/game_edit.html', {'form': form, 'game': game})


@staff_required
def products_list(request):
    products = Product.objects.all().order_by('title')
    form = ProductForm()
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Продукт добавлен.')
            return redirect('staff:products')
    return render(request, 'staff/products_list.html', {'products': products, 'form': form})


@staff_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Продукт обновлен.')
        return redirect('staff:products')
    return render(request, 'staff/product_edit.html', {'form': form, 'product': product})


@staff_required
def settings_view(request):
    settings = SiteSettings.get_solo()
    form = SiteSettingsForm(request.POST or None, request.FILES or None, instance=settings)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Настройки сохранены.')
        return redirect('staff:settings')

    weekly = WeeklySchedule.objects.all()
    specials = SpecialDay.objects.all()
    return render(
        request,
        'staff/settings.html',
        {'form': form, 'weekly': weekly, 'specials': specials},
    )


@staff_required
def weekly_schedule_create(request):
    form = WeeklyScheduleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'График добавлен.')
        return redirect('staff:settings')
    return render(request, 'staff/weekly_schedule_form.html', {'form': form})


@staff_required
def special_day_create(request):
    form = SpecialDayForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Особый день добавлен.')
        return redirect('staff:settings')
    return render(request, 'staff/special_day_form.html', {'form': form})


@staff_required
def manual_booking(request):
    form = ReservationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Бронирование создано.')
        return redirect('staff:reservations')
    return render(request, 'staff/manual_booking.html', {'form': form})
