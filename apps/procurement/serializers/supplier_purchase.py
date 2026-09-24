from decimal import Decimal

from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer
from apps.organization.models import Organization
from apps.warehouse.models import Warehouse

from ..models import Supplier, SupplierPurchase
from ..services import create_supplier_purchase_with_items
from .supplier_purchase_item import (
    SupplierPurchaseItemInputSerializer,
    SupplierPurchaseItemSerializer,
)


class SupplierPurchaseSerializer(BaseModelSerializer):
    """Xarid hujjati uchun serializer — bog'liq obyektlar nested qaytariladi."""

    class Meta:
        model = SupplierPurchase
        fields = [
            "id",
            "document_number",
            "organization",
            "supplier",
            "warehouse",
            "created_by",
            "status",
            "total_amount",
            "paid_amount",
            "debt_amount",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "organization": {"fields": ["id", "name"]},
            "supplier": {"fields": ["id", "name"]},
            "warehouse": {"fields": ["id", "name"]},
            "created_by": {"fields": ["id", "full_name"]},
        }


class SupplierPurchaseDetailSerializer(SupplierPurchaseSerializer):
    """Bitta xarid hujjatini qatorlari (`items`) bilan birga qaytarish uchun — `retrieve`."""

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["items"] = SupplierPurchaseItemSerializer(
            instance.items.select_related("product_party"),
            many=True,
            context=self.context,
        ).data
        return data


class SupplierPurchaseCreateSerializer(serializers.Serializer):
    """Xarid hujjatini barcha qatorlari bilan bitta so'rovda yaratish uchun."""

    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.active()
    )
    supplier = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.active())
    warehouse = serializers.PrimaryKeyRelatedField(queryset=Warehouse.objects.active())
    paid_amount = serializers.DecimalField(
        max_digits=15, decimal_places=2, required=False, default=Decimal(0)
    )
    items = SupplierPurchaseItemInputSerializer(many=True)

    def validate_items(self, value):
        """Ro'yxat bo'sh bo'lmasligini tekshiradi."""
        if not value:
            raise serializers.ValidationError("Kamida bitta qator bo'lishi kerak.")
        return value

    def create(self, validated_data):
        return create_supplier_purchase_with_items(**validated_data)

    def to_representation(self, instance):
        """Yaratilgan hujjatni qatorlari bilan birga, detail serializer orqali qaytaradi."""
        return SupplierPurchaseDetailSerializer(instance, context=self.context).data


class SupplierPurchaseUpdateSerializer(serializers.Serializer):
    """Xarid hujjati header'ini yangilash uchun — `items` bu yerda yo'q, qatorlar
    alohida `purchase-items/` endpointi orqali boshqariladi. `status` ham bu yerda
    yo'q — u ombor qoldig'iga ta'sir qilgani uchun faqat `confirm`/`revert`
    action'lari orqali o'zgaradi."""

    supplier = serializers.PrimaryKeyRelatedField(
        queryset=Supplier.objects.active(), required=False
    )
    warehouse = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.active(), required=False
    )
    paid_amount = serializers.DecimalField(
        max_digits=15, decimal_places=2, required=False
    )

    def update(self, instance, validated_data):
        """`paid_amount` o'zgarsa `debt_amount`ni qayta hisoblaydi."""
        for field_name in ("supplier", "warehouse"):
            if field_name in validated_data:
                setattr(instance, field_name, validated_data[field_name])

        if "paid_amount" in validated_data:
            instance.paid_amount = validated_data["paid_amount"]
            instance.debt_amount = instance.total_amount - instance.paid_amount

        instance.save()
        return instance

    def to_representation(self, instance):
        return SupplierPurchaseDetailSerializer(instance, context=self.context).data
