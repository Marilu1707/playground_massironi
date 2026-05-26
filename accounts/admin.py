from django.contrib import admin
from .models import PerfilUsuario


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('user', 'nivel', 'puntos', 'monedas', 'bio', 'link')
    list_editable = ('monedas', 'puntos')
    search_fields = ('user__username', 'bio')
    readonly_fields = ('nivel',)
    ordering = ('-monedas',)
