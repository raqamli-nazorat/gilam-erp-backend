from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
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
from ..serializers.recruitment_dismissal import (
    ensure_employee_has_single_active_record,
    ensure_employee_not_employed,
    ensure_recruitment_date_after_dismissal,
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
    action_permissions = {
        "approve": ["hr.change_recruitmentdismissal"],
        "cancel": ["hr.change_recruitmentdismissal"],
    }

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

    @action(detail=False, methods=["get"])
    def count(self, request):
        queryset = self.filter_queryset(self.get_queryset())

        def status_counts(records):
            return {
                "all": records.count(),
                "draft": records.filter(
                    status=RecruitmentDismissal.Status.DRAFT
                ).count(),
                "approved": records.filter(
                    status=RecruitmentDismissal.Status.APPROVED
                ).count(),
                "cancelled": records.filter(
                    status=RecruitmentDismissal.Status.CANCELLED
                ).count(),
            }

        return Response(
            {
                "recruitments": status_counts(
                    queryset.filter(type=RecruitmentDismissal.Type.RECRUITMENT)
                ),
                "dismissals": status_counts(
                    queryset.filter(type=RecruitmentDismissal.Type.DISMISSAL)
                ),
            }
        )

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
        """Xodimni ishdan bo'shatish — `employee` tanlanadi, faqat sabab kiritiladi."""
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
        """Bir nechta xodimni bitta so'rovda, umumiy sabab bilan ishdan bo'shatish uchun."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instances = serializer.save()

        output_serializer = RecruitmentDismissalSerializer(
            instances, many=True, context=self.get_serializer_context()
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        instance = self.get_object()
        if instance.status != RecruitmentDismissal.Status.DRAFT:
            raise ValidationError(
                {"status": ["Faqat qoralama yozuvni tasdiqlash mumkin."]}
            )

        with transaction.atomic():
            if instance.type == RecruitmentDismissal.Type.RECRUITMENT:
                ensure_employee_not_employed(instance.employee)
                ensure_recruitment_date_after_dismissal(
                    instance.employee, instance.rec_dism_date
                )
            else:
                source = ensure_employee_has_single_active_record(instance.employee)
                instance.branch = source.branch
                instance.position = source.position
                instance.card_number = source.card_number
                instance.salary_type = source.salary_type
                instance.fix_summa = source.fix_summa
                instance.fix_percent = source.fix_percent

            instance.status = RecruitmentDismissal.Status.APPROVED
            instance._actor = request.user
            instance.save()

        return Response(
            RecruitmentDismissalSerializer(
                instance, context=self.get_serializer_context()
            ).data
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        instance = self.get_object()
        if instance.status != RecruitmentDismissal.Status.DRAFT:
            raise ValidationError(
                {"status": ["Faqat qoralama yozuvni bekor qilish mumkin."]}
            )

        instance.status = RecruitmentDismissal.Status.CANCELLED
        instance.save(update_fields=["status", "updated_at"])
        return Response(
            RecruitmentDismissalSerializer(
                instance, context=self.get_serializer_context()
            ).data
        )
