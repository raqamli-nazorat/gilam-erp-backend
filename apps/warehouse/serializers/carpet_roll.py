from apps.base.serializers import BaseModelSerializer

from ..models import CarpetRoll


class CarpetRollSerializer(BaseModelSerializer):
    """Rulon uchun serializer — mahsulot partiyasi va ombor nested qaytariladi."""

    class Meta:
        model = CarpetRoll
        fields = [
            "id",
            "product_party",
            "warehouse",
            "roll_number",
            "initial_length_meters",
            "current_length_meters",
            "is_offcut",
            "status",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "product_party": {"fields": ["id", "name"]},
            "warehouse": {"fields": ["id", "name"]},
        }
