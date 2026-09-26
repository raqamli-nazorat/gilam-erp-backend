from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import CalculatingSalary


@admin.register(CalculatingSalary)
class CalculatingSalaryAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "branch",
        "employee",
        "for_month",
        "amount",
        "currency",
        "status",
        "is_active",
    )
    list_filter = ("is_active", "status", "for_month", "branch", "currency")
    search_fields = ("employee__full_name", "branch__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("branch", "employee", "currency")
