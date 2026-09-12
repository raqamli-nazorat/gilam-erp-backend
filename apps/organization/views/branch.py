from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.base.views import BaseManageViewSet

from ..filters import BranchFilter
from ..models import Branch
from ..serializers import BranchSerializer
from ..services import get_branch_status_counts


class BranchViewSet(BaseManageViewSet):

    queryset = Branch.objects.active().select_related(
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
    action_permissions = {
        "close": ["organization.close_branch"],
        "open": ["organization.open_branch"],
    }

    def get_queryset(self):
        if self.action in ["close", "open"]:
            qs = Branch.objects.all().select_related(
                "organization", "region", "district"
            ).annotate(
                warehouses_count=Count(
                    "warehouses", filter=Q(warehouses__is_active=True), distinct=True
                )
            )
            user = getattr(self.request, "user", None)
            if user and not getattr(user, "is_system_admin", False):
                accessible_ids = user.get_accessible_branches(
                    include_inactive=True
                ).values_list("id", flat=True)
                qs = qs.filter(id__in=accessible_ids)
            return qs
        return super().get_queryset()

    @action(detail=False, methods=["get"])
    def counts(self, request):
        return Response(get_branch_status_counts())

    @action(detail=True, methods=["patch"])
    def close(self, request, pk=None):
        branch = self.get_object()
        branch.is_active = False
        branch.save(update_fields=["is_active", "updated_at"])
        return Response(
            {
                "id": str(branch.id),
                "name": branch.name,
                "is_active": branch.is_active,
                "detail": "Filial yopildi.",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["patch"])
    def open(self, request, pk=None):
        branch = self.get_object()
        branch.is_active = True
        branch.save(update_fields=["is_active", "updated_at"])
        return Response(
            {
                "id": str(branch.id),
                "name": branch.name,
                "is_active": branch.is_active,
                "detail": "Filial qayta ochildi.",
            },
            status=status.HTTP_200_OK,
        )
