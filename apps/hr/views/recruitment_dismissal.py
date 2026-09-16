from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.base.views import BaseManageViewSet

from ..filters import RecruitmentDismissalFilter
from ..models import RecruitmentDismissal
from ..serializers import (
    RecruitmentDismissalBulkCreateSerializer,
    RecruitmentDismissalSerializer,
)


class RecruitmentDismissalViewSet(BaseManageViewSet):
    queryset = RecruitmentDismissal.objects.active().select_related(
        "branch", "employee", "position"
    )
    serializer_class = RecruitmentDismissalSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RecruitmentDismissalFilter
    search_fields = [
        "employee__full_name",
        "employee__phone_number",
        "position__name",
        "branch__name",
        "card_number",
        "dismissal_reason",
    ]
    ordering_fields = ["rec_dism_date", "created_at"]

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request, *args, **kwargs):
        """Bir nechta xodimni bitta so'rovda ishga olish/bo'shatish uchun."""
        serializer = RecruitmentDismissalBulkCreateSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        instances = serializer.save()

        output_serializer = RecruitmentDismissalSerializer(
            instances, many=True, context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
