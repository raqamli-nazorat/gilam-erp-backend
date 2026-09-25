from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import WorkSchedule, WorkScheduleItem


class WorkScheduleSerializer(BaseModelSerializer):
    status = serializers.SerializerMethodField(read_only=True)

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

    def validate(self, attrs):
        """Sana va vaqt oralig'i to'g'riligini tekshiradi."""
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
