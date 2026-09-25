from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import AccrualRetention


class AccrualRetentionSerializer(BaseModelSerializer):
    """Hisoblash / ushlab qolish uchun serializer — valyuta nested qaytariladi."""

    class Meta:
        model = AccrualRetention
        fields = [
            "id",
            "name",
            "type",
            "currency",
            "value",
            "created_at",
            "updated_at",
        ]
        related_fields = {"currency": {"fields": ["id", "name", "short_name"]}}

    def validate(self, attrs):
        """Qiymat manfiy emasligini, foiz turida esa 100 dan oshmasligini tekshiradi."""
        value = attrs.get("value", getattr(self.instance, "value", None))
        type_ = attrs.get("type", getattr(self.instance, "type", None))
        if value is not None and value < 0:
            raise serializers.ValidationError(
                {"value": "Qiymat manfiy bo'lmasligi kerak."}
            )
        if type_ == AccrualRetention.Type.PERCENT and value is not None and value > 100:
            raise serializers.ValidationError(
                {"value": "Foiz qiymati 100 dan oshmasligi kerak."}
            )
        return attrs
