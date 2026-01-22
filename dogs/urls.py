from django.urls import path
from . import views

urlpatterns = [
    # Public / client-facing
    path("", views.client_home, name="client_home"),
    path("dogs/<int:pk>/", views.client_dog_detail, name="client_dog_detail"),
    path("dogs/<int:pk>/photo/", views.dog_photo_bytes, name="dog_photo_bytes"),

    # NEW: adoption actions
    path("dogs/<int:pk>/request-adoption/", views.request_adoption, name="request_adoption"),
    path("adoptions/<int:request_id>/review/", views.review_adoption_request, name="review_adoption_request"),
    path("profile/", views.profile, name="profile"),


    # Profile
    path("profile/<int:user_id>/", views.admin_view_profile, name="admin_view_profile"),

    # Favourites
    path("favourites/", views.my_favourites, name="my_favourites"),
    path(
        "dogs/<int:pk>/favourite/",
        views.add_to_favourites,
        name="add_to_favourites",
    ),
    path(
        "dogs/<int:pk>/unfavourite/",
        views.remove_from_favourites,
        name="remove_from_favourites",
    ),

    # Internal/admin dashboard & actions
    path("admin-home/", views.home, name="home"),
    path("add/", views.add_dog, name="add_dog"),
    path("edit/<int:pk>/", views.edit_dog, name="edit_dog"),
    path("delete/<int:pk>/", views.delete_dog, name="delete_dog"),
    path("details/<int:pk>/", views.view_dog, name="view_dog"),
]
