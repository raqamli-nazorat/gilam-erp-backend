from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import SupplierPurchase


@admin.register(SupplierPurchase)
class SupplierPurchaseAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "organization",
        "supplier",
        "warehouse",
        "total_amount",
        "paid_amount",
        "debt_amount",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "organization", "supplier", "warehouse", "created_at")
    search_fields = ("supplier__name", "warehouse__name", "organization__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("organization", "supplier", "warehouse")
