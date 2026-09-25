from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import CurrencyFilter, CurrencyLedgerFilter
from ..models import Currency, CurrencyLedger
from ..serializers import CurrencyLedgerSerializer, CurrencySerializer


class CurrencyViewSet(BaseManageViewSet):
    """Valyutalar uchun CRUD ViewSet."""

    queryset = Currency.objects.active()
    serializer_class = CurrencySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CurrencyFilter
    search_fields = ["name", "short_name"]
    ordering_fields = ["name", "short_name", "created_at"]


class CurrencyLedgerViewSet(BaseManageViewSet):
    """Valyuta kurslari uchun CRUD ViewSet."""

    queryset = CurrencyLedger.objects.select_related("currency").active()
    serializer_class = CurrencyLedgerSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CurrencyLedgerFilter
    search_fields = ["currency__name", "currency__short_name"]
    ordering_fields = ["day", "value", "created_at"]
