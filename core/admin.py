from django.contrib import admin
from .models import Mensaje


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('remitente', 'asunto', 'fecha', 'leido')
    list_filter = ('leido',)
    search_fields = ('remitente__username', 'asunto')
    readonly_fields = ('remitente', 'asunto', 'cuerpo', 'fecha')
