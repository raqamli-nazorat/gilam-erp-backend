from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.base.views import BaseManageViewSet

from ..filters import OrganizationFilter
from ..models import Organization
from ..serializers import OrganizationSerializer
from ..services import get_organization_status_counts


class OrganizationViewSet(BaseManageViewSet):

    queryset = Organization.objects.active().select_related("region", "district").annotate(
        branches_count=Count(
            "branches", filter=Q(branches__is_active=True), distinct=True
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
