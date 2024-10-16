from django.urls import path
from . import views

urlpatterns = [
    path('data_lxc_list/', views.data_lxc_list, name='data_lxc_list'),
    path('metrics_containers/', views.metrics_containers, name='metrics_containers')
]
