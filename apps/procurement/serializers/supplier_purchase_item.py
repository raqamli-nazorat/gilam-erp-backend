from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer
from apps.catalog.models import Design, ProductColor, ProductParty, Quality, Unit

from ..models import SupplierPurchase, SupplierPurchaseItem
from ..services import create_purchase_item, update_purchase_item


class SupplierPurchaseItemSerializer(BaseModelSerializer):
    """Xarid qatori uchun serializer — bog'liq obyektlar nested qaytariladi."""

    class Meta:
        model = SupplierPurchaseItem
        fields = [
            "id",
            "purchase",
            "product_party",
            "roll_number",
            "width",
            "length",
            "quantity",
            "total_length_meters",
            "price_per_sqm",
            "subtotal",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "purchase": {"fields": ["id"]},
            "product_party": {"fields": ["id", "name"]},
        }


class SupplierPurchaseProductPartyInputSerializer(serializers.Serializer):
    """Qator ichida yangi mahsulot partiyasini yaratish uchun — `branch` ombordan avtomatik olinadi."""

    name = serializers.CharField(max_length=100)
    quality = serializers.PrimaryKeyRelatedField(queryset=Quality.objects.active())
    design = serializers.PrimaryKeyRelatedField(queryset=Design.objects.active())
    color = serializers.PrimaryKeyRelatedField(queryset=ProductColor.objects.active())
    unit = serializers.PrimaryKeyRelatedField(queryset=Unit.objects.active())
    description = serializers.CharField(required=False, allow_blank=True, default="")
    party_number = serializers.CharField(required=False, allow_blank=True, default="")
    barcode = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    is_runner = serializers.BooleanField(required=False, default=False)
    price_per_sqm_purchase = serializers.DecimalField(max_digits=15, decimal_places=2)
    price_per_sqm_sale = serializers.DecimalField(max_digits=15, decimal_places=2)


class SupplierPurchaseItemInputSerializer(serializers.Serializer):
    """Xarid hujjati qatori — mavjud yoki yangi mahsulot partiyasi bilan."""

    product_party = serializers.PrimaryKeyRelatedField(
        queryset=ProductParty.objects.active(), required=False
    )
    product_party_data = SupplierPurchaseProductPartyInputSerializer(required=False)
    roll_number = serializers.CharField(required=False, allow_blank=True, default="")
    width = serializers.DecimalField(max_digits=8, decimal_places=2)
    length = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False, allow_null=True
    )
    quantity = serializers.IntegerField(required=False, default=1)
    total_length_meters = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    price_per_sqm = serializers.DecimalField(max_digits=15, decimal_places=2)

    def validate(self, attrs):
        """`product_party` yoki `product_party_data`dan faqat bittasi kelishi shart."""
        has_existing = bool(attrs.get("product_party"))
        has_new = bool(attrs.get("product_party_data"))
        if has_existing == has_new:
            raise serializers.ValidationError(
                "Har bir qatorda 'product_party' yoki 'product_party_data' dan"
                " faqat bittasi bo'lishi kerak."
            )
        return attrs


class SupplierPurchaseItemCreateSerializer(SupplierPurchaseItemInputSerializer):
    """Mavjud xarid hujjatiga yangi qator qo'shish uchun — `purchase` qo'shiladi.

    Saqlangach hujjatning `total_amount`/`debt_amount`i avtomatik qayta hisoblanadi.
    """

    purchase = serializers.PrimaryKeyRelatedField(
        queryset=SupplierPurchase.objects.active()
    )

    def create(self, validated_data):
        return create_purchase_item(**validated_data)

    def to_representation(self, instance):
        return SupplierPurchaseItemSerializer(instance, context=self.context).data


class SupplierPurchaseItemUpdateSerializer(serializers.Serializer):
    """Mavjud qatorni yangilash uchun — `product_party` bu yerda o'zgartirilmaydi.

    `subtotal` va hujjatning `total_amount`/`debt_amount`i avtomatik qayta hisoblanadi.
    """

    roll_number = serializers.CharField(required=False, allow_blank=True)
    width = serializers.DecimalField(max_digits=8, decimal_places=2, required=False)
    length = serializers.DecimalField(
        max_digits=8, decimal_places=2, required=False, allow_null=True
    )
    quantity = serializers.IntegerField(required=False)
    total_length_meters = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, allow_null=True
    )
    price_per_sqm = serializers.DecimalField(
        max_digits=15, decimal_places=2, required=False
    )

    def update(self, instance, validated_data):
        return update_purchase_item(instance, **validated_data)

    def to_representation(self, instance):
        return SupplierPurchaseItemSerializer(instance, context=self.context).data
