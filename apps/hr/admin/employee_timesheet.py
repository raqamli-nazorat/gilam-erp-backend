from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import EmployeeTimesheet, EmployeeTimesheetItem


class EmployeeTimesheetItemInline(admin.TabularInline):
    model = EmployeeTimesheetItem
    extra = 0
    autocomplete_fields = ("employee",)


@admin.register(EmployeeTimesheet)
class EmployeeTimesheetAdmin(BaseModelAdmin):
    list_display = ("id", "branch", "for_month", "status", "is_active", "created_at")
    list_filter = ("is_active", "status", "for_month", "branch")
    search_fields = ("branch__name",)
    ordering = ("-created_at",)
    autocomplete_fields = ("branch",)
    inlines = [EmployeeTimesheetItemInline]


@admin.register(EmployeeTimesheetItem)
class EmployeeTimesheetItemAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "employee_timesheet",
        "employee",
        "date",
        "work_hour_in_plan",
        "work_hour_in_fact",
        "is_active",
    )
    list_filter = ("is_active", "employee_timesheet")
    search_fields = ("employee__full_name", "employee__phone_number")
    ordering = ("-date",)
    autocomplete_fields = ("employee_timesheet", "employee")
