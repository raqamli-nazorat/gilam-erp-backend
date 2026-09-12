from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import RegionFilter
from ..models import Region
from ..serializers import RegionSerializer


class RegionViewSet(BaseManageViewSet):

    queryset = Region.objects.active().select_related("country")
    serializer_class = RegionSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RegionFilter
    search_fields = ["name", "country__name"]
    ordering_fields = ["name", "created_at"]
