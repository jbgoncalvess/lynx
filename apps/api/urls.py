from django.urls import path
from . import views

urlpatterns = [
    path('info_containers/', views.info_containers, name='info_containers')
]
