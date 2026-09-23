from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import ProductPartyFilter
from ..models import ProductParty
from ..serializers import ProductPartySerializer


class ProductPartyViewSet(BaseManageViewSet):
    """Mahsulot partiyasi uchun CRUD ViewSet."""

    queryset = ProductParty.objects.select_related(
        "branch", "quality", "design", "color", "unit"
    ).active()
    serializer_class = ProductPartySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductPartyFilter
    search_fields = ["name", "party_number", "barcode"]
    ordering_fields = ["name", "created_at", "price_per_sqm_sale"]
