from django.urls import path

from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('reservations/', views.reservations_list, name='reservations'),
    path('reservations/<int:reservation_id>/status/', views.reservation_status, name='reservation_status'),
    path('reservations/manual/', views.manual_booking, name='manual_booking'),
    path('tables/', views.table_list, name='tables'),
    path('tables/<int:table_id>/', views.table_edit, name='table_edit'),
    path('messages/', views.messages_list, name='messages'),
    path('catalog/games/', views.games_list, name='games'),
    path('catalog/games/<int:game_id>/', views.game_edit, name='game_edit'),
    path('catalog/products/', views.products_list, name='products'),
    path('catalog/products/<int:product_id>/', views.product_edit, name='product_edit'),
    path('settings/', views.settings_view, name='settings'),
    path('settings/weekly/new/', views.weekly_schedule_create, name='weekly_schedule_create'),
    path('settings/special/new/', views.special_day_create, name='special_day_create'),
]
