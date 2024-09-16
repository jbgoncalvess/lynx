from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name='home'),
    path('home/', views.base, name='home')
]

