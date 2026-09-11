from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.base.views import BaseManageViewSet

from ..filters import OrganizationFilter
from ..models import Organization
from ..serializers import OrganizationSerializer
from ..services import get_organization_status_counts


class OrganizationViewSet(BaseManageViewSet):
    """Tashkilotlar uchun CRUD ViewSet."""

    queryset = Organization.objects.select_related("region", "district").annotate(
        branches_count=Count(
            "branches", filter=Q(branches__is_active=True), distinct=True
        )
    )
    serializer_class = OrganizationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OrganizationFilter
    search_fields = ["name", "inn", "phone", "director"]
    ordering_fields = ["name", "created_at"]

    @action(detail=False, methods=["get"])
    def counts(self, request):
        """Faol va to'xtatilgan tashkilotlar sonini qaytaradi."""
        return Response(get_organization_status_counts())
