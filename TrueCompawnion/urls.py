from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dogs.views import client_home, signup  # ← import signup

urlpatterns = [
    path("", client_home, name="client_home"),          # public homepage
    path("dogs/", include("dogs.urls")),                # app routes
    path("accounts/", include("django.contrib.auth.urls")),  # login/logout/etc
    path("accounts/signup/", signup, name="signup"),    # ← add this line
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
