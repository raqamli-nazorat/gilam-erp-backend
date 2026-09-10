"""
Autentifikatsiya view'lari — tizimga kirish va access tokenni yangilash.

Ushbu view'lar `apps/accounts/auth_urls.py` orqali `/api/v1/auth/` ostiga ulanadi.
CRUD `UserViewSet` dan ajratilgan: login oqimi resurs emas, alohida endpoint.
"""

from drf_spectacular.utils import extend_schema
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.utils.throttles import (
    CustomScopedRateThrottle,
    ThrottleExceptionHandlerMixin,
)

from ..serializers import LoginSerializer


@extend_schema(tags=["Auth"], summary="Tizimga kirish")
class LoginView(ThrottleExceptionHandlerMixin, TokenObtainPairView):
    """
    `phone_number` + `password` orqali access/refresh token va `user` ni qaytaradi.

    `login` scope bo'yicha throttle qo'llanadi (IP + telefon raqami bo'yicha 5/15m).
    Nofaol (`is_active=False`) foydalanuvchi SimpleJWT tomonidan rad etiladi (401).
    """

    serializer_class = LoginSerializer
    throttle_classes = [CustomScopedRateThrottle]
    throttle_scope = "login"


@extend_schema(tags=["Auth"], summary="Access tokenni yangilash")
class RefreshTokenView(TokenRefreshView):
    """Amaldagi `refresh` token orqali yangi `access` token beradi."""

    serializer_class = TokenRefreshSerializer
