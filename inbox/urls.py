from django.urls import path

from . import views

app_name = 'inbox'

urlpatterns = [
    path('contact/', views.contact, name='contact'),
]
