from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.base.views import BaseManageViewSet

from ..filters import RecruitmentDismissalFilter
from ..models import RecruitmentDismissal
from ..serializers import (
    EmployeeDismissalSerializer,
    EmployeeRecruitmentSerializer,
    RecruitmentDismissalBulkCreateSerializer,
    RecruitmentDismissalBulkDismissSerializer,
    RecruitmentDismissalListSerializer,
    RecruitmentDismissalSerializer,
)


class RecruitmentDismissalViewSet(BaseManageViewSet):
    queryset = RecruitmentDismissal.objects.active().select_related(
        "branch", "employee", "employee__organization", "position"
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

    def get_serializer_class(self):
        """Action'ga qarab tegishli serializer qaytaradi.

        `create`/`bulk_create` — faqat ishga olish uchun (`type` body'da yo'q,
        avtomatik "recruitment" qo'yiladi). `dismiss`/`bulk_dismiss` — faqat
        ishdan bo'shatish uchun.
        """
        if self.action == "list":
            return RecruitmentDismissalListSerializer
        if self.action == "create":
            return EmployeeRecruitmentSerializer
        if self.action == "dismiss":
            return EmployeeDismissalSerializer
        if self.action == "bulk_create":
            return RecruitmentDismissalBulkCreateSerializer
        if self.action == "bulk_dismiss":
            return RecruitmentDismissalBulkDismissSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        """Ishga olish yozuvini yaratadi, javobda to'liq (`type` bilan) yozuvni qaytaradi."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        output_serializer = RecruitmentDismissalSerializer(
            serializer.instance, context=self.get_serializer_context()
        )
        headers = self.get_success_headers(output_serializer.data)
        return Response(
            output_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(detail=False, methods=["post"])
    def dismiss(self, request, *args, **kwargs):
        """Xodimni ishdan bo'shatish — `employee` tanlanadi, faqat sabab va asos hujjat kiritiladi."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        output_serializer = RecruitmentDismissalSerializer(
            instance, context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request, *args, **kwargs):
        """Bir nechta xodimni bitta so'rovda ishga olish uchun."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instances = serializer.save()

        output_serializer = RecruitmentDismissalSerializer(
            instances, many=True, context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="bulk-dismiss")
    def bulk_dismiss(self, request, *args, **kwargs):
        """Bir nechta xodimni bitta so'rovda, umumiy sabab/hujjat bilan ishdan bo'shatish uchun."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instances = serializer.save()

        output_serializer = RecruitmentDismissalSerializer(
            instances, many=True, context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
