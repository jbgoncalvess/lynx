from django.urls import path
from . import views

urlpatterns = [
    path('num_containers/', views.num_containers, name='num_containers'),
    path('metrics_containers/', views.metrics_containers, name='metrics_containers')
]
