from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.base.mixins import AutoSchemaMixin
from apps.utils.throttles import (
    CustomScopedRateThrottle,
    ThrottleExceptionHandlerMixin,
)

from ..serializers.auth import LoginSerializer, RefreshTokenSerializer


class LoginView(AutoSchemaMixin, ThrottleExceptionHandlerMixin, TokenObtainPairView):
    serializer_class = LoginSerializer
    throttle_classes = [CustomScopedRateThrottle]
    throttle_scope = "login"


class RefreshTokenView(AutoSchemaMixin, TokenRefreshView):
    serializer_class = RefreshTokenSerializer

