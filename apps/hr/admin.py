from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from .models import (
    Employee,
    EmployeeLedger,
    Position,
    RecruitmentDismissal,
    WorkSchedule,
    WorkScheduleItem,
)


@admin.register(Employee)
class EmployeeAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "branch",
        "full_name",
        "region",
        "district",
        "address",
        "passport_seria",
        "passport_number",
        "jsshr",
        "stir",
        "phone_number",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "branch", "region", "district", "created_at")
    search_fields = (
        "full_name",
        "address",
        "passport_seria",
        "passport_number",
        "jsshr",
        "stir",
        "phone_number",
        "description",
        "branch__name",
        "region__name",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("branch", "region", "district")


@admin.register(EmployeeLedger)
class EmployeeLedgerAdmin(BaseModelAdmin):
    list_display = ("id", "branch", "employee", "type", "is_active", "created_at")
    list_filter = ("is_active", "branch", "type", "created_at")
    search_fields = ("branch__name", "employee__phone_number", "employee__full_name")
    ordering = ("-created_at",)
    autocomplete_fields = ("branch", "employee")


@admin.register(Position)
class PositionAdmin(BaseModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "description")
    ordering = ("-created_at",)


@admin.register(RecruitmentDismissal)
class RecruitmentDismissalAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "type",
        "branch",
        "employee",
        "position",
        "card_number",
        "card_image",
        "salary_type",
        "fix_summa",
        "fix_percent",
        "rec_dism_date",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_active",
        "type",
        "branch",
        "position",
        "salary_type",
        "created_at",
    )
    search_fields = (
        "card_number",
        "card_image",
        "dismissal_reason",
        "branch__name",
        "employee__phone_number",
        "employee__full_name",
        "position__name",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("branch", "employee", "position")


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
