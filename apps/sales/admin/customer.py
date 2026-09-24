from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import Customer


@admin.register(Customer)
class CustomerAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "organization",
        "full_name",
        "phone",
        "balance_debt",
        "loyalty_discount_pct",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "organization", "created_at")
    search_fields = ("full_name", "phone", "address", "organization__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("organization",)
