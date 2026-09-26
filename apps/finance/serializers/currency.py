from django.utils import timezone
from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..constants import CURRENCY_NAMES
from ..models import Currency, CurrencyLedger


class CurrencySerializer(BaseModelSerializer):
    """Valyuta uchun serializer — `short_name` Markaziy bankdagi valyutalardan bo'lishi shart."""

    class Meta:
        model = Currency
        fields = ["id", "name", "short_name", "created_at", "updated_at"]

    def validate_short_name(self, value):
        """Valyuta bankda borligini va avval yaratilmaganini tekshiradi."""
        value = value.upper()
        if Currency.objects.active().filter(short_name=value).exists():
            raise serializers.ValidationError("Bu valyuta allaqachon yaratilgan.")
        if value not in CURRENCY_NAMES:
            raise serializers.ValidationError(
                "Bunday valyuta bank ro'yxatida topilmadi. Qidirish: /currencies/available/?search="
            )
        return value


class CurrencyLedgerSerializer(BaseModelSerializer):
    """Valyuta kursi (so'mga nisbatan) — faqat o'qish uchun, valyuta nested qaytariladi."""

    class Meta:
        model = CurrencyLedger
        fields = ["id", "currency", "value", "day", "created_at", "updated_at"]
        related_fields = {"currency": {"fields": ["id", "name", "short_name"]}}


class CurrencySyncSerializer(serializers.Serializer):
    """Bank kursi olinadigan sana (bo'sh bo'lsa — bugun)."""

    day = serializers.DateField(required=False)

    def validate_day(self, value):
        """Kelajak sanasi kiritilmasligini tekshiradi."""
        if value > timezone.localdate():
            raise serializers.ValidationError("Kelajak sanasi uchun kurs mavjud emas.")
        return value
