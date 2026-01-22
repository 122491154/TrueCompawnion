from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dogs import views as dogs_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/logout/", dogs_views.logout_view, name="logout"),
    path("accounts/signup/", dogs_views.signup, name="signup"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("dogs.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
