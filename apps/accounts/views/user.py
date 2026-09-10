from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import UserFilter
from ..models import User
from ..serializers import UserSerializer


# TODO: vaqtinchalik Swagger'dan yashirilgan — API stabillashgach `exclude=True` olib tashlanadi.
@extend_schema(exclude=True)
class UserViewSet(BaseManageViewSet):
    """
    Foydalanuvchilar uchun CRUD ViewSet.

    Autentifikatsiya (login / token refresh) alohida — `apps/accounts/auth_urls.py`.
    """

    queryset = User.objects.active().select_related("role", "branch")
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    search_fields = ["full_name", "phone_number"]
    ordering_fields = ["full_name", "created_at"]
