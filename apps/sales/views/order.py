from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import OrderFilter
from ..models import Order
from ..serializers import OrderSerializer


class OrderViewSet(BaseManageViewSet):
    """Sotuv cheklari uchun CRUD ViewSet."""

    queryset = Order.objects.select_related(
        "organization", "branch", "customer", "seller", "cashier"
    ).active()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OrderFilter
    search_fields = ["customer__full_name", "seller__full_name"]
    ordering_fields = ["created_at", "final_amount"]
