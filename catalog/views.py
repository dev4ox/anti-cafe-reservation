from django.shortcuts import render

from .models import BoardGame, Product


def games_list(request):
    games = BoardGame.objects.filter(is_available=True)
    return render(request, 'catalog/games_list.html', {'games': games})


def products_list(request):
    products = Product.objects.filter(is_available=True)
    return render(request, 'catalog/products_list.html', {'products': products})
