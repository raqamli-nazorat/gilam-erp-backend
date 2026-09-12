from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import PositionFilter
from ..models import Position
from ..serializers import PositionSerializer


class PositionViewSet(BaseManageViewSet):
    """Lavozimlar uchun CRUD ViewSet."""

    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = PositionFilter
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
