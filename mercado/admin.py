from django.contrib import admin
from .models import Transaccion, CompraReceta

_TRANSACCION_FIELDS = ('usuario', 'tipo', 'monto', 'descripcion', 'referencia_queso', 'referencia_post', 'fecha')
_COMPRA_FIELDS = ('comprador', 'post', 'monto_pagado', 'fecha')


@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'monto', 'descripcion', 'fecha')
    list_filter = ('tipo', 'fecha')
    search_fields = ('usuario__username', 'descripcion')
    date_hierarchy = 'fecha'
    ordering = ('-fecha',)
    # El historial es un audit log inmutable — nunca se edita
    readonly_fields = _TRANSACCION_FIELDS

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(CompraReceta)
class CompraRecetaAdmin(admin.ModelAdmin):
    list_display = ('comprador', 'post', 'monto_pagado', 'fecha')
    list_filter = ('fecha',)
    search_fields = ('comprador__username', 'post__titulo')
    date_hierarchy = 'fecha'
    ordering = ('-fecha',)
    readonly_fields = _COMPRA_FIELDS

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
