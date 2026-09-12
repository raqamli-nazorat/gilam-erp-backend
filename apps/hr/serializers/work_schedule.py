from django.db import transaction

from apps.base.serializers import BaseModelSerializer

from ..models import WorkSchedule, WorkScheduleItem


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
        extra_kwargs = {
            "work_schedule": {"required": False},
        }


class WorkScheduleSerializer(BaseModelSerializer):
    items = WorkScheduleItemSerializer(many=True, required=False)

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
            "items",
            "created_at",
            "updated_at",
        ]
        related_fields = {
            "branch": {"fields": ["id", "name"]},
        }

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        schedule = WorkSchedule.objects.create(**validated_data)
        for item_data in items_data:
            item_data.pop("work_schedule", None)
            WorkScheduleItem.objects.create(work_schedule=schedule, **item_data)
        return schedule

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        schedule = super().update(instance, validated_data)
        if items_data is not None:
            schedule.items.all().delete()
            for item_data in items_data:
                item_data.pop("work_schedule", None)
                WorkScheduleItem.objects.create(work_schedule=schedule, **item_data)
        return schedule
