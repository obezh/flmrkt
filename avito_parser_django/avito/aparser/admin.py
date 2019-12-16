from django.contrib import admin

from .forms import ProductForm
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'price', 'currency', 'published_date', 'url')
    list_filter = ('currency', 'published_date')
    form = ProductForm
