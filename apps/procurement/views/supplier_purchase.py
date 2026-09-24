from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import SupplierPurchaseFilter
from ..models import SupplierPurchase
from ..serializers import SupplierPurchaseSerializer


class SupplierPurchaseViewSet(BaseManageViewSet):
    """Xarid hujjatlari uchun CRUD ViewSet."""

    queryset = SupplierPurchase.objects.select_related(
        "organization", "supplier", "warehouse"
    ).active()
    serializer_class = SupplierPurchaseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SupplierPurchaseFilter
    search_fields = ["supplier__name", "warehouse__name"]
    ordering_fields = ["created_at", "total_amount"]
