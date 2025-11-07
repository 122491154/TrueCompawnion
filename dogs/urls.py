from django.urls import path
from . import views
from .views import client_home, client_dog_detail, dog_photo_bytes

urlpatterns = [
    # 🐶 Public catalogue (default homepage)
    path("", client_home, name="client_home"),  # now loads when users go to /

    # 🐾 Public dog detail pages
    path("dogs/<int:pk>/", client_dog_detail, name="client_dog_detail"),
    path("dogs/<int:pk>/photo/", dog_photo_bytes, name="dog_photo_bytes"),  # optional binary photo route

    # 👩‍💼 Internal/admin dashboard & actions
    path("admin-home/", views.home, name="home"),  # admin dashboard
    path("add/", views.add_dog, name="add_dog"),
    path("edit/<int:pk>/", views.edit_dog, name="edit_dog"),
    path("delete/<int:pk>/", views.delete_dog, name="delete_dog"),
    path("details/<int:pk>/", views.view_dog, name="view_dog"),
]
