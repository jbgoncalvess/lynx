from django.urls import path
from . import views

urlpatterns = [
    path('data_lxc_list/', views.data_lxc_list, name='data_lxc_list'),
    path('data_lxc_image/', views.data_lxc_image, name='data_lxc_image'),
    path('metrics_containers/', views.metrics_containers, name='metrics_containers')
]
