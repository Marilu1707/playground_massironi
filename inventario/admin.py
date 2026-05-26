from django.contrib import admin
from .models import Queso


@admin.register(Queso)
class QuesoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'precio_monedas', 'stock', 'etiqueta_stock')
    list_editable = ('precio', 'precio_monedas', 'stock')
    list_filter = ('stock',)
    search_fields = ('nombre', 'descripcion')
    ordering = ('nombre',)
