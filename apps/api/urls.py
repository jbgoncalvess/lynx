from django.urls import path
from . import views

urlpatterns = [
    path('api/lxc_list/', views.lxc_list, name='lxc_list'),
    path('api/lxc_image/', views.lxc_image, name='lxc_image'),
    path('api/metrics/', views.metrics, name='metrics')
]
