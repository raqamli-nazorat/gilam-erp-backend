from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import CounterpartyFilter
from ..models import Counterparty
from ..serializers import CounterpartySerializer


class CounterpartyViewSet(BaseManageViewSet):
    """Kontragentlar uchun CRUD ViewSet."""

    queryset = Counterparty.objects.select_related("type").active()
    serializer_class = CounterpartySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CounterpartyFilter
    search_fields = ["name", "phone_number", "type__name"]
    ordering_fields = ["name", "phone_number", "created_at"]
