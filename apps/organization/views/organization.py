from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
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

    def get_queryset(self):
        if self.action in ["suspend", "activate"]:
            return Organization.objects.all().select_related("region", "district").annotate(
                branches_count=Count(
                    "branches", filter=Q(branches__is_active=True), distinct=True
                )
            )
        return super().get_queryset()

    @action(detail=False, methods=["get"])
    def counts(self, request):
        return Response(get_organization_status_counts())

    @action(detail=True, methods=["patch"])
    def suspend(self, request, pk=None):
        if not getattr(request.user, "is_system_admin", False):
            raise PermissionDenied("Faqat tizim administratori tashkilotni to'xtata oladi.")
        organization = self.get_object()
        organization.is_active = False
        organization.save(update_fields=["is_active", "updated_at"])
        return Response(
            {
                "id": str(organization.id),
                "name": organization.name,
                "is_active": organization.is_active,
                "detail": "Tashkilot faoliyati to'xtatildi.",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["patch"])
    def activate(self, request, pk=None):
        if not getattr(request.user, "is_system_admin", False):
            raise PermissionDenied("Faqat tizim administratori tashkilotni faollashtira oladi.")
        organization = self.get_object()
        organization.is_active = True
        organization.save(update_fields=["is_active", "updated_at"])
        return Response(
            {
                "id": str(organization.id),
                "name": organization.name,
                "is_active": organization.is_active,
                "detail": "Tashkilot faoliyati faollashtirildi.",
            },
            status=status.HTTP_200_OK,
        )
