from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import OrganizationFilter
from ..models import Organization
from ..serializers import OrganizationSerializer


class OrganizationViewSet(BaseManageViewSet):
    """Tashkilotlar uchun CRUD ViewSet."""

    queryset = Organization.objects.active().select_related("region", "district")
    serializer_class = OrganizationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OrganizationFilter
    search_fields = ["name", "inn", "phone", "director"]
    ordering_fields = ["name", "created_at"]
