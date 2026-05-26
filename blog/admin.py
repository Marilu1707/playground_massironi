from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'es_premium', 'precio_monedas', 'fecha')
    list_filter = ('autor', 'precio_monedas', 'fecha')
    search_fields = ('titulo', 'cuerpo', 'subtitulo')
    ordering = ('-fecha',)
    readonly_fields = ('preview', 'fecha')
    fieldsets = (
        (None, {
            'fields': ('titulo', 'subtitulo', 'autor', 'imagen'),
        }),
        ('Contenido', {
            'fields': ('cuerpo',),
        }),
        ('Monetización', {
            'fields': ('precio_monedas', 'preview'),
            'description': 'Si precio > 0, el preview se genera automáticamente.',
        }),
        ('Metadata', {
            'fields': ('fecha',),
            'classes': ('collapse',),
        }),
    )
