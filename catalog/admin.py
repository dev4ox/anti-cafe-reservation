from django.contrib import admin

from .models import BoardGame, Product


@admin.register(BoardGame)
class BoardGameAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_available')
    list_editable = ('is_available',)
    search_fields = ('title',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'is_available')
    list_editable = ('is_available',)
    search_fields = ('title',)
