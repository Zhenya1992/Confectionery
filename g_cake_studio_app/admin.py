from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Класс продуктов в админке"""

    list_display = ('name', 'slug', 'price', 'is_available', 'created_at')
    list_filter = ('is_available', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)