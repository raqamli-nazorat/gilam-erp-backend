from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import WarehouseFilter
from ..models import Warehouse
from ..serializers import WarehouseSerializer


class WarehouseViewSet(BaseManageViewSet):
    """Omborlar uchun CRUD ViewSet."""

    queryset = Warehouse.objects.select_related("branch").active()
    serializer_class = WarehouseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = WarehouseFilter
    search_fields = ["name", "address", "branch__name"]
    ordering_fields = ["name", "created_at"]
