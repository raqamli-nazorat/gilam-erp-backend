from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import SupplierFilter
from ..models import Supplier
from ..serializers import SupplierSerializer


class SupplierViewSet(BaseManageViewSet):
    """Yetkazuvchilar uchun CRUD ViewSet."""

    queryset = Supplier.objects.select_related("organization").active()
    serializer_class = SupplierSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SupplierFilter
    search_fields = ["name", "phone", "address"]
    ordering_fields = ["name", "created_at"]
