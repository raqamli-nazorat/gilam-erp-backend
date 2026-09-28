from django.db.models import Count, Q
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.base.views import BaseManageViewSet

from ..filters import AccrualRetentionDocumentFilter
from ..models import AccrualRetentionDocument
from ..serializers import (
    AccrualRetentionDocumentBulkCreateSerializer,
    AccrualRetentionDocumentCancelSerializer,
    AccrualRetentionDocumentCountSerializer,
    AccrualRetentionDocumentSerializer,
)
from ..services.accrual_document import (
    approve_document,
    cancel_document,
    ensure_draft,
)


class AccrualRetentionDocumentViewSet(BaseManageViewSet):
    """Xodimga hisoblash / ushlab qolish belgilash hujjatlari uchun ViewSet."""

    queryset = AccrualRetentionDocument.objects.active().select_related(
        "branch", "employee", "accrual_retention"
    )
    serializer_class = AccrualRetentionDocumentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AccrualRetentionDocumentFilter
    search_fields = [
        "employee__full_name",
        "employee__phone_number",
        "accrual_retention__name",
    ]
    ordering_fields = ["date", "created_at", "updated_at"]
    action_permissions = {
        "count": ["finance.view_accrualretentiondocument"],
        "approve": ["finance.change_accrualretentiondocument"],
        "cancel": ["finance.change_accrualretentiondocument"],
    }

    def get_queryset(self):
        """Detail uchun xodimning tashkiloti va akkauntini qo'shimcha so'rovsiz oladi."""
        queryset = super().get_queryset()
        if self.action == "retrieve":
            queryset = queryset.select_related(
                "employee__organization", "employee__user_account"
            )
        return queryset

    def get_serializer_class(self):
        """`bulk_create` uchun alohida serializer qaytaradi."""
        if self.action == "bulk_create":
            return AccrualRetentionDocumentBulkCreateSerializer
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        """Faqat qoralama hujjatni o'chirishga ruxsat beradi."""
        ensure_draft(instance)
        super().perform_destroy(instance)

    @extend_schema(
        summary="Statuslar bo'yicha hujjatlar soni",
        request=None,
        responses={200: AccrualRetentionDocumentCountSerializer},
    )
    @action(detail=False, methods=["get"])
    def count(self, request, *args, **kwargs):
        """Barchasi, qoralama, tasdiqlangan va bekor qilingan hujjatlar sonini qaytaradi."""
        Status = AccrualRetentionDocument.Status
        counts = self.get_queryset().aggregate(
            all=Count("pk"),
            draft=Count("pk", filter=Q(status=Status.DRAFT)),
            approved=Count("pk", filter=Q(status=Status.APPROVED)),
            cancelled=Count("pk", filter=Q(status=Status.CANCELLED)),
        )
        return Response(counts)

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request, *args, **kwargs):
        """Bir turni bir nechta xodimga bir so'rovda belgilaydi (hammasi yoki hech narsa)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        documents = serializer.save()
        output = AccrualRetentionDocumentSerializer(
            documents, many=True, context=self.get_serializer_context()
        )
        return Response(output.data, status=status.HTTP_201_CREATED)

    @extend_schema(request=None, responses=AccrualRetentionDocumentSerializer)
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Qoralama hujjatni tasdiqlaydi."""
        document = approve_document(self.get_object())
        return Response(
            AccrualRetentionDocumentSerializer(
                document, context=self.get_serializer_context()
            ).data
        )

    @extend_schema(
        request=AccrualRetentionDocumentCancelSerializer,
        responses=AccrualRetentionDocumentSerializer,
    )
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Hujjatni bekor qiladi (sabab va PDF/Excel asos hujjat ixtiyoriy)."""
        serializer = AccrualRetentionDocumentCancelSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = cancel_document(self.get_object(), **serializer.validated_data)
        return Response(
            AccrualRetentionDocumentSerializer(
                document, context=self.get_serializer_context()
            ).data
        )
