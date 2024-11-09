from django.urls import path
from . import views

urlpatterns = [
    path('lxc_list/', views.lxc_list, name='lxc_list'),
    path('lxc_image/', views.lxc_image, name='lxc_image'),
    path('metrics_containers/', views.metrics_containers, name='metrics_containers')
]
