from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import Weekday, WorkSchedule, WorkScheduleItem


class WorkScheduleSerializer(BaseModelSerializer):
    status = serializers.SerializerMethodField(read_only=True)
    work_days = serializers.ListField(
        child=serializers.ChoiceField(
            choices=Weekday.choices,
            error_messages={
                "invalid_choice": "Ish kuni 0 dan 6 gacha bo'lishi kerak.",
            },
        ),
        allow_empty=True,
        help_text="0=Dushanba, 1=Seshanba, 2=Chorshanba, 3=Payshanba, "
        "4=Juma, 5=Shanba, 6=Yakshanba",
    )

    class Meta:
        model = WorkSchedule
        fields = [
            "id",
            "branch",
            "name",
            "description",
            "from_date",
            "to_date",
            "from_hour",
            "to_hour",
            "work_days",
            "status",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "branch": {"fields": ["id", "name"]},
        }

    def get_status(self, obj):
        """`is_active`ni `Holati` sifatida ochiq qaytaradi (BaseModelSerializer uni yashiradi)."""
        return obj.is_active

    def validate_work_days(self, value):
        """Ish kunlari bo'sh yoki takroriy bo'lmasligini tekshirib, saralab qaytaradi."""
        if not value:
            raise serializers.ValidationError("Kamida bitta ish kuni tanlanishi kerak.")
        if len(value) != len(set(value)):
            raise serializers.ValidationError("Ish kunlari takrorlanmasligi kerak.")
        return sorted(value)

    def validate(self, attrs):
        """Sana va vaqt oralig'i to'g'riligini tekshiradi."""
        from_hour = attrs.get("from_hour", getattr(self.instance, "from_hour", None))
        to_hour = attrs.get("to_hour", getattr(self.instance, "to_hour", None))
        if from_hour and to_hour and from_hour >= to_hour:
            raise serializers.ValidationError(
                {"to_hour": "Ish tugashi boshlanishidan keyin bo'lishi kerak."}
            )
        from_date = attrs.get("from_date", getattr(self.instance, "from_date", None))
        to_date = attrs.get("to_date", getattr(self.instance, "to_date", None))
        if from_date and to_date and from_date > to_date:
            raise serializers.ValidationError(
                {
                    "to_date": "Tugash sanasi boshlanish sanasidan oldin bo'lmasligi kerak."
                }
            )
        return attrs


class WorkScheduleItemSerializer(BaseModelSerializer):
    class Meta:
        model = WorkScheduleItem
        fields = [
            "id",
            "work_schedule",
            "name",
            "day_type",
            "day_date",
            "from_hour",
            "to_hour",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "work_schedule": {"fields": ["id", "name"]},
        }
