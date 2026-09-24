from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, extend_schema, extend_schema_view
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.base.views import BaseManageViewSet

from ..filters import SupplierPurchaseFilter
from ..models import SupplierPurchase
from ..serializers import (
    SupplierPurchaseCreateSerializer,
    SupplierPurchaseDetailSerializer,
    SupplierPurchaseSerializer,
    SupplierPurchaseUpdateSerializer,
)
from ..services import confirm_supplier_purchase, revert_supplier_purchase

CREATE_EXAMPLE = OpenApiExample(
    "Namuna: mavjud va yangi mahsulot partiyasi bilan kirim",
    summary="1-qator — mavjud `product_party` tanlanadi, 2-qator — `product_party_data`"
    " bilan yangisi yaratiladi (branch omborning filialidan avtomatik olinadi).",
    description="`organization`, `supplier`, `warehouse` — majburiy. `items` ichida har"
    " bir qatorda `product_party` YOKI `product_party_data`dan faqat bittasi bo'lishi"
    " kerak. `subtotal`, `total_amount`, `debt_amount`, `document_number`,"
    " `created_by` klientdan yuborilmaydi — backend avtomatik hisoblaydi/beradi.",
    value={
        "organization": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "supplier": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "warehouse": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "paid_amount": "0.00",
        "items": [
            {
                "product_party": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "roll_number": "",
                "width": "4.00",
                "length": "30.00",
                "quantity": 1,
                "price_per_sqm": "50000.00",
            },
            {
                "product_party_data": {
                    "name": "400X3000",
                    "quality": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "design": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "color": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "unit": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "is_runner": True,
                    "price_per_sqm_purchase": "50000.00",
                    "price_per_sqm_sale": "60000.00",
                },
                "roll_number": "R-014",
                "width": "4.00",
                "length": "30.00",
                "quantity": 1,
                "price_per_sqm": "50000.00",
            },
        ],
    },
    request_only=True,
)


@extend_schema_view(create=extend_schema(examples=[CREATE_EXAMPLE]))
class SupplierPurchaseViewSet(BaseManageViewSet):
    """Xarid hujjatlari uchun CRUD ViewSet.

    `create` — hujjat va uning barcha qatorlarini (kerak bo'lsa yangi mahsulot
    partiyalari bilan birga) bitta so'rovda yaratadi (`SupplierPurchaseCreateSerializer`).
    `retrieve` — hujjatni qatorlari (`items`) bilan birga qaytaradi
    (`SupplierPurchaseDetailSerializer`); `list` esa eskidek faqat header.
    `update`/`partial_update` — faqat header (`supplier`/`warehouse`/`paid_amount`);
    qatorlar `purchase-items/` endpointi orqali alohida boshqariladi, o'zgarishlarda
    `total_amount`/`debt_amount` avtomatik qayta hisoblanadi. `status` bu yerda
    yo'q — faqat `confirm`/`revert` action'lari orqali o'zgaradi (ombor qoldig'iga
    ta'sir qilgani uchun).
    """

    queryset = SupplierPurchase.objects.select_related(
        "organization", "supplier", "warehouse", "created_by"
    ).active()
    serializer_class = SupplierPurchaseSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SupplierPurchaseFilter
    search_fields = ["document_number", "supplier__name", "warehouse__name"]
    ordering_fields = ["created_at", "total_amount"]

    def get_serializer_class(self):
        if self.action == "create":
            return SupplierPurchaseCreateSerializer
        if self.action in ("retrieve", "confirm", "revert"):
            return SupplierPurchaseDetailSerializer
        if self.action in ("update", "partial_update"):
            return SupplierPurchaseUpdateSerializer
        return super().get_serializer_class()

    @extend_schema(request=None)
    @action(detail=True, methods=["post"])
    def confirm(self, request, *args, **kwargs):
        """Hujjatni tasdiqlaydi — ombor qoldig'ini oshiradi, `StockTransaction`/
        `CarpetRoll` yaratadi."""
        purchase = confirm_supplier_purchase(self.get_object())
        return Response(self.get_serializer(purchase).data)

    @extend_schema(request=None)
    @action(detail=True, methods=["post"])
    def revert(self, request, *args, **kwargs):
        """Hujjatni qoralamaga qaytaradi — ombor qoldig'ini kamaytiradi va
        `StockTransaction`/`CarpetRoll`ni bekor qiladi."""
        purchase = revert_supplier_purchase(self.get_object())
        return Response(self.get_serializer(purchase).data)
