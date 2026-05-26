from django.urls import path
from . import views

urlpatterns = [
    path('', views.mercado_home, name='mercado_home'),
    path('comprar/queso/<int:pk>/', views.comprar_queso, name='comprar_queso'),
    path('comprar/receta/<int:pk>/', views.comprar_receta, name='comprar_receta'),
    path('historial/', views.historial, name='historial'),
    path('canjear/', views.canjear_puntos, name='canjear_puntos'),
]
