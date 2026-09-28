from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.base.views import BaseManageViewSet

from ..filters import CalculatingSalaryFilter
from ..models import CalculatingSalary
from ..serializers import (
    CalculatingSalaryCalculateSerializer,
    CalculatingSalaryCancelSerializer,
    CalculatingSalaryCountSerializer,
    CalculatingSalarySerializer,
)
from ..services.salary import (
    approve_salary,
    calculate_salaries,
    cancel_salary,
    ensure_draft,
)


class CalculatingSalaryViewSet(BaseManageViewSet):
    """Xodimlar oylik hisobi (oylik hisoblash hujjati) uchun ViewSet."""

    queryset = CalculatingSalary.objects.active().select_related(
        "branch", "employee", "currency"
    )
    serializer_class = CalculatingSalarySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CalculatingSalaryFilter
    search_fields = ["employee__full_name", "employee__phone_number", "branch__name"]
    ordering_fields = ["for_month", "amount", "created_at", "updated_at"]
    action_permissions = {
        "count": ["hr.view_calculatingsalary"],
        "approve": ["hr.change_calculatingsalary"],
        "cancel": ["hr.change_calculatingsalary"],
    }

    def get_serializer_class(self):
        """`calculate` uchun alohida serializer qaytaradi."""
        if self.action == "calculate":
            return CalculatingSalaryCalculateSerializer
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        """Faqat qoralama oylikni o'chirishga ruxsat beradi."""
        ensure_draft(instance)
        super().perform_destroy(instance)

    @extend_schema(
        summary="Statuslar bo'yicha oylik hisoblar soni",
        request=None,
        responses={200: CalculatingSalaryCountSerializer},
    )
    @action(detail=False, methods=["get"])
    def count(self, request, *args, **kwargs):
        """Barchasi, qoralama, tasdiqlangan va bekor qilingan oyliklar sonini qaytaradi."""
        Status = CalculatingSalary.Status
        counts = self.get_queryset().aggregate(
            all=Count("pk"),
            draft=Count("pk", filter=Q(status=Status.DRAFT)),
            approved=Count("pk", filter=Q(status=Status.APPROVED)),
            cancelled=Count("pk", filter=Q(status=Status.CANCELLED)),
        )
        return Response(counts)

    @action(detail=False, methods=["post"])
    def calculate(self, request, *args, **kwargs):
        """Filial va oy bo'yicha ishlayotgan xodimlar oyligini avtomatik hisoblaydi."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        salaries, skipped = calculate_salaries(
            data["branch"], int(data["for_month"]), data["year"]
        )
        ids = [salary.pk for salary in salaries]
        output = CalculatingSalarySerializer(
            self.get_queryset().filter(pk__in=ids),
            many=True,
            context=self.get_serializer_context(),
        )
        return Response({"salaries": output.data, "skipped": skipped})

    @extend_schema(request=None, responses=CalculatingSalarySerializer)
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Qoralama oylikni tasdiqlaydi."""
        salary = approve_salary(self.get_object())
        return Response(
            CalculatingSalarySerializer(
                salary, context=self.get_serializer_context()
            ).data
        )

    @extend_schema(
        request=CalculatingSalaryCancelSerializer, responses=CalculatingSalarySerializer
    )
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Oylikni bekor qiladi (sabab va PDF/Excel asos hujjat ixtiyoriy)."""
        serializer = CalculatingSalaryCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        salary = cancel_salary(self.get_object(), **serializer.validated_data)
        return Response(
            CalculatingSalarySerializer(
                salary, context=self.get_serializer_context()
            ).data
        )
