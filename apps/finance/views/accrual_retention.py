from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import AccrualRetentionFilter
from ..models import AccrualRetention
from ..serializers import AccrualRetentionSerializer


class AccrualRetentionViewSet(BaseManageViewSet):
    """Hisoblash / ushlab qolishlar uchun CRUD ViewSet."""

    queryset = AccrualRetention.objects.select_related("currency").active()
    serializer_class = AccrualRetentionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AccrualRetentionFilter
    search_fields = ["name", "currency__short_name"]
    ordering_fields = ["name", "value", "created_at"]
