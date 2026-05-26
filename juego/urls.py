from django.urls import path
from . import views

urlpatterns = [
    path('',        views.juego_list,   name='juego_list'),
    path('nuevo/',  views.juego_create, name='juego_create'),
    path('jugar/',  views.juego_game,   name='juego_game'),
    path('puntuar/', views.puntuar,     name='juego_puntuar'),
]
