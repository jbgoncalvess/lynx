from django.urls import path
from . import views

urlpatterns = [
    path('images/', views.images_view, name='images'),
    path('images/delete-image/<str:image_name>/', views.delete_image, name='delete_image')
]