from django.contrib import admin
from .models import Pedido


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'queso', 'cantidad', 'puntos_ganados', 'completado', 'fecha')
    list_filter = ('completado', 'fecha')
    search_fields = ('usuario__username', 'queso__nombre')
    ordering = ('-fecha',)
