from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import DebtLedger


@admin.register(DebtLedger)
class DebtLedgerAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "organization",
        "customer",
        "order",
        "total_debt",
        "remaining_debt",
        "status",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "status", "organization", "created_at")
    search_fields = ("customer__full_name", "organization__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("organization", "customer", "order")
