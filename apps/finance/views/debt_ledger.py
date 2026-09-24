from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import DebtLedgerFilter
from ..models import DebtLedger
from ..serializers import DebtLedgerSerializer


class DebtLedgerViewSet(BaseManageViewSet):
    """Nasiya daftari uchun CRUD ViewSet."""

    queryset = DebtLedger.objects.select_related(
        "organization", "customer", "order"
    ).active()
    serializer_class = DebtLedgerSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DebtLedgerFilter
    search_fields = ["customer__full_name"]
    ordering_fields = ["created_at", "remaining_debt"]
