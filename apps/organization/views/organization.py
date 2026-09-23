from django.db.models import Count, Prefetch, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.base.views import BaseManageViewSet

from ..filters import OrganizationFilter
from ..models import Branch, Organization
from ..serializers import OrganizationSerializer
from ..services import get_organization_status_counts


class OrganizationViewSet(BaseManageViewSet):
    queryset = (
        Organization.objects.active()
        .select_related("region", "district")
        .annotate(
            branches_count=Count(
                "branches", filter=Q(branches__is_active=True), distinct=True
            ),
            branches_active_count=Count(
                "branches",
                filter=Q(branches__is_active=True, branches__is_closed=False),
                distinct=True,
            ),
            branches_closed_count=Count(
                "branches",
                filter=Q(branches__is_active=True, branches__is_closed=True),
                distinct=True,
            ),
        )
    )
    serializer_class = OrganizationSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = OrganizationFilter
    search_fields = ["name", "inn", "phone", "director"]
    ordering_fields = ["name", "created_at"]
    action_permissions = {
        "suspend": ["organization.suspend_organization"],
        "activate": ["organization.activate_organization"],
    }

    def get_queryset(self):
        """`TenantBranchScopeMixin` skoupidan keyin, detal uchun filiallar ro'yxatini prefetch qiladi."""
        queryset = super().get_queryset()

        if self.action == "retrieve":
            queryset = queryset.prefetch_related(
                Prefetch(
                    "branches",
                    queryset=Branch.objects.active().order_by("name"),
                ),
            )

        return queryset

    @property
    def serializer_fields(self):
        """Ro'yxatda filiallar ro'yxatini (N+1 oldini olish uchun) chiqarmaydi."""
        if self.action == "list":
            return [
                "id",
                "name",
                "inn",
                "phone",
                "director",
                "region",
                "district",
                "address",
                "prefix",
                "is_suspended",
                "suspension_reason",
                "branches_count",
                "branches_active_count",
                "branches_closed_count",
                "created_at",
                "updated_at",
            ]
        return None

    @action(detail=False, methods=["get"])
    def counts(self, request):
        return Response(get_organization_status_counts())

    @action(detail=True, methods=["patch"])
    def suspend(self, request, pk=None):
        reason = request.data.get("reason") or request.data.get("suspension_reason")
        if not reason or not str(reason).strip():
            return Response(
                {"reason": ["To'xtatish sababini kiritish majburiy."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        organization = self.get_object()
        organization.is_suspended = True
        organization.suspension_reason = str(reason).strip()
        organization.save(
            update_fields=["is_suspended", "suspension_reason", "updated_at"]
        )
        return Response(
            {
                "id": str(organization.id),
                "name": organization.name,
                "is_suspended": organization.is_suspended,
                "suspension_reason": organization.suspension_reason,
                "detail": "Tashkilot faoliyati to'xtatildi.",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["patch"])
    def activate(self, request, pk=None):
        organization = self.get_object()
        organization.is_suspended = False
        organization.suspension_reason = ""
        organization.save(
            update_fields=["is_suspended", "suspension_reason", "updated_at"]
        )
        return Response(
            {
                "id": str(organization.id),
                "name": organization.name,
                "is_suspended": organization.is_suspended,
                "suspension_reason": organization.suspension_reason,
                "detail": "Tashkilot faoliyati faollashtirildi.",
            },
            status=status.HTTP_200_OK,
        )
