from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import SupplierPurchase


@admin.register(SupplierPurchase)
class SupplierPurchaseAdmin(BaseModelAdmin):
    list_display = (
        "document_number",
        "organization",
        "supplier",
        "warehouse",
        "status",
        "created_by",
        "total_amount",
        "paid_amount",
        "debt_amount",
        "is_active",
        "created_at",
    )
    list_filter = (
        "status",
        "is_active",
        "organization",
        "supplier",
        "warehouse",
        "created_at",
    )
    search_fields = (
        "document_number",
        "supplier__name",
        "warehouse__name",
        "organization__name",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("organization", "supplier", "warehouse", "created_by")
