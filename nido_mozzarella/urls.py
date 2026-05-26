"""
URLs principales del proyecto Nido Mozzarella.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ── Admin personalizado ──────────────────────────────────────────────────────
admin.site.site_header  = "🧀 Nido Mozzarella"
admin.site.site_title   = "Nido Admin"
admin.site.index_title  = "Panel de administración"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('pages/', include('blog.urls')),
    path('inventario/', include('inventario.urls')),
    path('juego/', include('juego.urls')),
    path('mercado/', include('mercado.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
