from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import RoleFilter
from ..models import Role
from ..serializers import RoleSerializer


# TODO: vaqtinchalik Swagger'dan yashirilgan — API stabillashgach `exclude=True` olib tashlanadi.
@extend_schema(exclude=True)
class RoleViewSet(BaseManageViewSet):
    """Rollar uchun CRUD ViewSet."""

    queryset = Role.objects.active()
    serializer_class = RoleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RoleFilter
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
