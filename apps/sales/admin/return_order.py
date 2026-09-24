from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import ReturnOrder


@admin.register(ReturnOrder)
class ReturnOrderAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "organization",
        "branch",
        "order",
        "customer",
        "refund_amount",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "organization", "branch", "created_at")
    search_fields = ("customer__full_name", "reason", "organization__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("organization", "branch", "order", "customer")
