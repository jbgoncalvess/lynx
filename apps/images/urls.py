from django.urls import path
from . import views

urlpatterns = [
    path('images/', views.images_view, name='images')
]