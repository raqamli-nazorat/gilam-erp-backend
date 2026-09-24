from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from apps.base.views import BaseManageViewSet

from ..filters import StockTransactionFilter
from ..models import StockTransaction
from ..serializers import StockTransactionSerializer


class StockTransactionViewSet(BaseManageViewSet):
    """Ombor harakatlari uchun CRUD ViewSet."""

    queryset = StockTransaction.objects.select_related(
        "organization", "product_party", "roll", "from_warehouse", "to_warehouse"
    ).active()
    serializer_class = StockTransactionSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = StockTransactionFilter
    ordering_fields = ["created_at"]
