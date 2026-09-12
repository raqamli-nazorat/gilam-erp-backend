from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import DistrictFilter
from ..models import District
from ..serializers import DistrictSerializer


class DistrictViewSet(BaseManageViewSet):
    queryset = District.objects.active().select_related("region")
    serializer_class = DistrictSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DistrictFilter
    search_fields = ["name", "region__name"]
    ordering_fields = ["name", "created_at"]
    safe_methods_unrestricted = True

