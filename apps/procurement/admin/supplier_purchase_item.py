from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import SupplierPurchaseItem


@admin.register(SupplierPurchaseItem)
class SupplierPurchaseItemAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "purchase",
        "product_party",
        "roll_number",
        "width",
        "length",
        "subtotal",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "created_at")
    search_fields = ("roll_number", "product_party__name", "purchase__supplier__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("purchase", "product_party")
