from django.urls import path
from . import views

urlpatterns = [
    path('containers/', views.containers_view, name='containers'),
    path('info_containers/', views.containers_view, name='info_containers')
]
