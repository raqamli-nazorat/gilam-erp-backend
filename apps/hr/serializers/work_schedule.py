from rest_framework import serializers

from apps.base.serializers import BaseModelSerializer

from ..models import WorkSchedule


class WorkScheduleSerializer(BaseModelSerializer):
    status = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = WorkSchedule
        fields = [
            "id",
            "name",
            "description",
            "from_hour",
            "to_hour",
            "days",
            "status",
            "created_at",
            "updated_at",
        ]

    def get_status(self, obj):
        """`is_active`ni `Holati` sifatida ochiq qaytaradi (BaseModelSerializer uni yashiradi)."""
        return obj.is_active
