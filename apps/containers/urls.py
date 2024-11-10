from django.urls import path
from . import views

urlpatterns = [
    path('containers/', views.containers_view, name='containers'),
    path('containers/start-container/<str:container_name>/', views.start_container, name='start-container'),
    path('containers/stop-container/<str:container_name>/', views.stop_container, name='stop-container'),
    path('containers/restart-container/<str:container_name>/', views.restart_container, name='restart-container'),
    path('containers/swap-ipv4/<str:container_name>/', views.swap_ip, name='swap-ipv4'),
    path('containers/toggle-ipv6/<str:container_name>/', views.toggle_ipv6, name='toggle-ipv6'),
]
