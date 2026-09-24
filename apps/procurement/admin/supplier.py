from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import Supplier


@admin.register(Supplier)
class SupplierAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "organization",
        "name",
        "phone",
        "balance_debt",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "organization", "created_at")
    search_fields = ("name", "phone", "address", "organization__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("organization",)
