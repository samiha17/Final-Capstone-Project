from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Frontend / normal views
    path(
        "", include("news.urls")
    ),  # all news app frontend routes like /articles/, /register/
    # API routes
    path("api/", include("news.urls")),  # only DRF router URLs will work here
    # JWT auth
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
