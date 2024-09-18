from django.urls import path
from . import views

urlpatterns = [
    path('containers/', views.containers_view, name='containers'),
    path('info_containers/', views.info_containers, name='info_containers')
]
