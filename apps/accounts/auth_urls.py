"""
Autentifikatsiya (`/api/v1/auth/`) uchun URL'lar — login va token yangilash.

`apps/urls.py` da `path("auth/", include("apps.accounts.auth_urls"))` orqali ulanadi.
"""

from django.urls import path

from .views.auth import LoginView, RefreshTokenView

urlpatterns = [
    path("login/", LoginView.as_view(), name="auth-login"),
    path("token/refresh/", RefreshTokenView.as_view(), name="auth-token-refresh"),
]
