from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import Currency, CurrencyLedger


class CurrencySerializer(BaseModelSerializer):
    """Valyuta uchun serializer."""

    class Meta:
        model = Currency
        fields = ["id", "name", "short_name", "created_at", "updated_at"]


class CurrencyLedgerSerializer(BaseModelSerializer):
    """Valyuta kursi (so'mga nisbatan) uchun serializer — valyuta nested qaytariladi."""

    class Meta:
        model = CurrencyLedger
        fields = ["id", "currency", "value", "day", "created_at", "updated_at"]
        related_fields = {"currency": {"fields": ["id", "name", "short_name"]}}

    def validate_value(self, value):
        """Kurs manfiy bo'lmasligini tekshiradi."""
        if value < 0:
            raise serializers.ValidationError("Kurs qiymati manfiy bo'lmasligi kerak.")
        return value
