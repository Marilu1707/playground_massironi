from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('messages/', views.messages_list, name='messages_list'),
    path('messages/new/', views.new_message, name='new_message'),
]
