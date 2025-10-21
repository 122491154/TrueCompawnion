from django.urls import path
from . import views

urlpatterns = [
    path('', views.dog_list, name='dog_list'),
    path('add/', views.add_dog, name='add_dog'),
    path('edit/<int:dog_id>/', views.edit_dog, name='edit_dog'),  # 👈 NEW
    path('delete/<int:dog_id>/', views.delete_dog, name='delete_dog'),
]
