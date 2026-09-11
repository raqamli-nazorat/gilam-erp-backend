from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.base.views import BaseManageViewSet

from ..filters import BranchFilter
from ..models import Branch
from ..serializers import BranchSerializer
from ..services import get_branch_status_counts


class BranchViewSet(BaseManageViewSet):
    """Filiallar uchun CRUD ViewSet."""

    queryset = Branch.objects.select_related(
        "organization", "region", "district"
    ).annotate(
        warehouses_count=Count(
            "warehouses", filter=Q(warehouses__is_active=True), distinct=True
        )
    )
    serializer_class = BranchSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BranchFilter
    search_fields = ["name", "phone", "address", "organization__name"]
    ordering_fields = ["name", "created_at"]

    @action(detail=False, methods=["get"])
    def counts(self, request):
        """Faol va yopilgan filiallar sonini qaytaradi."""
        return Response(get_branch_status_counts())
