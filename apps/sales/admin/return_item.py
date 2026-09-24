from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import ReturnItem


@admin.register(ReturnItem)
class ReturnItemAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "return_order",
        "order_item",
        "quantity",
        "length_meters",
        "restock_status",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "restock_status", "created_at")
    search_fields = ("order_item__product_party__name",)
    ordering = ("-created_at",)
    autocomplete_fields = ("return_order", "order_item")
