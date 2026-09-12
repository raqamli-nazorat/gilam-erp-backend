from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import WorkSchedule, WorkScheduleItem


@admin.register(WorkSchedule)
class WorkScheduleAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "branch",
        "name",
        "from_date",
        "to_date",
        "from_hour",
        "to_hour",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "branch", "created_at")
    search_fields = ("name", "description", "branch__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("branch",)


@admin.register(WorkScheduleItem)
class WorkScheduleItemAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "work_schedule",
        "name",
        "day_type",
        "day_date",
        "from_hour",
        "to_hour",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "day_type", "created_at")
    search_fields = ("name", "work_schedule__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("work_schedule",)
