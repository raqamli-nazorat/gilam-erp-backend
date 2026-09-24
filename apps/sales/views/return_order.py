from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import ReturnOrderFilter
from ..models import ReturnOrder
from ..serializers import ReturnOrderSerializer


class ReturnOrderViewSet(BaseManageViewSet):
    """Qaytarish hujjatlari uchun CRUD ViewSet."""

    queryset = ReturnOrder.objects.select_related(
        "organization", "branch", "order", "customer"
    ).active()
    serializer_class = ReturnOrderSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ReturnOrderFilter
    search_fields = ["customer__full_name", "reason"]
    ordering_fields = ["created_at", "refund_amount"]
