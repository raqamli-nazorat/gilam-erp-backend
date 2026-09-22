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
        "days",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    ordering = ("-created_at",)
