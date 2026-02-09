from django.urls import path

from . import views

app_name = 'booking'

urlpatterns = [
    path('', views.booking_index, name='index'),
    path('new/', views.booking_create, name='create'),
    path('success/', views.booking_success, name='success'),
    path('ticket/<str:public_code>/', views.booking_ticket, name='ticket'),
]
