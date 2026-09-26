from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.base.mixins import (
    AutoSchemaMixin,
    DynamicPermissionMixin,
    TenantBranchScopeMixin,
)

from ..filters import CurrencyFilter, CurrencyLedgerFilter
from ..models import Currency, CurrencyLedger
from ..serializers import (
    CurrencyLedgerSerializer,
    CurrencySerializer,
    CurrencySyncSerializer,
)
from ..services.currency import search_currencies, sync_ledgers


class CurrencyViewSet(
    AutoSchemaMixin,
    DynamicPermissionMixin,
    TenantBranchScopeMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Valyutalar: ro'yxat, bankdagi valyutalardan tanlab yaratish, o'chirish (soft delete) va qidirish."""

    queryset = Currency.objects.active()
    serializer_class = CurrencySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CurrencyFilter
    search_fields = ["name", "short_name"]
    ordering_fields = ["name", "short_name", "created_at"]

    @extend_schema(
        summary="Bankdagi valyutalarni qidirish",
        parameters=[
            OpenApiParameter("search", str, description="Valyuta kodi yoki nomi")
        ],
        responses={200: {"type": "array", "items": {"type": "object"}}},
    )
    @action(detail=False, methods=["get"], pagination_class=None)
    def available(self, request):
        """Markaziy bankdagi valyutalarni kod yoki nom bo'yicha qidiradi (`?search=usd`)."""
        created = set(self.get_queryset().values_list("short_name", flat=True))
        found = search_currencies(request.query_params.get("search", ""))
        return Response(
            [
                {
                    "short_name": item["short_name"],
                    "name": item["name"],
                    "exists": item["short_name"] in created,
                }
                for item in found
            ]
        )


class CurrencyLedgerViewSet(
    AutoSchemaMixin,
    DynamicPermissionMixin,
    TenantBranchScopeMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Valyuta kurslari: ro'yxat va Markaziy bankdan kursni olib saqlash."""

    queryset = CurrencyLedger.objects.select_related("currency").active()
    serializer_class = CurrencyLedgerSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = CurrencyLedgerFilter
    search_fields = ["currency__name", "currency__short_name"]
    ordering_fields = ["day", "value", "created_at"]

    @extend_schema(
        summary="Markaziy bank kursini olib saqlash",
        request=CurrencySyncSerializer,
        responses={200: CurrencyLedgerSerializer(many=True)},
    )
    @action(detail=False, methods=["post"])
    def sync(self, request):
        """Bank kursini olib, bazadagi valyutalar uchun ledger yaratadi/yangilaydi."""
        serializer = CurrencySyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        day = serializer.validated_data.get("day") or timezone.localdate()
        ledgers = sync_ledgers(day)
        return Response(
            {
                "day": day,
                "count": len(ledgers),
                "results": CurrencyLedgerSerializer(
                    ledgers, many=True, context=self.get_serializer_context()
                ).data,
            }
        )
