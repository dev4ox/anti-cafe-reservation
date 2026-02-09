from django.urls import path

from . import views

app_name = 'catalog'

urlpatterns = [
    path('games/', views.games_list, name='games'),
    path('products/', views.products_list, name='products'),
]
