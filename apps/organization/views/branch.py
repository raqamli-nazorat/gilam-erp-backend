from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import BranchFilter
from ..models import Branch
from ..serializers import BranchSerializer


class BranchViewSet(BaseManageViewSet):
    """Filiallar uchun CRUD ViewSet."""

    queryset = Branch.objects.active().select_related(
        "organization", "region", "district"
    )
    serializer_class = BranchSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BranchFilter
    search_fields = ["name", "phone", "organization__name"]
    ordering_fields = ["name", "created_at"]
