from apps.base.serializers import BaseModelSerializer

from ..models import ProductParty


class ProductPartySerializer(BaseModelSerializer):
    """Mahsulot partiyasi uchun serializer — filial, sifat, dizayn, rang, o'lchov nested qaytariladi."""

    class Meta:
        model = ProductParty
        fields = [
            "id",
            "branch",
            "party_number",
            "name",
            "quality",
            "design",
            "color",
            "unit",
            "description",
            "barcode",
            "is_runner",
            "price_per_sqm_purchase",
            "price_per_sqm_sale",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "branch": {"fields": ["id", "name"]},
            "quality": {"fields": ["id", "name"]},
            "design": {"fields": ["id", "name"]},
            "color": {"fields": ["id", "name"]},
            "unit": {"fields": ["id", "name"]},
        }
