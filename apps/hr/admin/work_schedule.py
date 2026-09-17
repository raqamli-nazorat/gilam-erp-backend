from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import WorkSchedule


@admin.register(WorkSchedule)
class WorkScheduleAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "name",
        "from_hour",
        "to_hour",
        "is_monday",
        "is_tuesday",
        "is_wednesday",
        "is_thursday",
        "is_friday",
        "is_saturday",
        "is_sunday",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    ordering = ("-created_at",)
