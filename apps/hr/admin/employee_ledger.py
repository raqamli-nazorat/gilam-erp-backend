from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import EmployeeLedger


@admin.register(EmployeeLedger)
class EmployeeLedgerAdmin(BaseModelAdmin):
    list_display = ("id", "branch", "employee", "type", "is_active", "created_at")
    list_filter = ("is_active", "branch", "type", "created_at")
    search_fields = ("branch__name", "employee__phone_number", "employee__full_name")
    ordering = ("-created_at",)
    autocomplete_fields = ("branch", "employee")
