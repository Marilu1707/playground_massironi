from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('<int:pageId>/', views.post_detail, name='post_detail'),
    path('crear/', views.post_create, name='post_create'),
    path('<int:pageId>/editar/', views.post_edit, name='post_edit'),
    path('<int:pageId>/eliminar/', views.post_delete, name='post_delete'),
]
