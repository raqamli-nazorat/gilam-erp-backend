from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import OrderItem


@admin.register(OrderItem)
class OrderItemAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "order",
        "product_party",
        "warehouse",
        "sqm",
        "final_item_price",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "warehouse", "created_at")
    search_fields = ("product_party__name", "order__customer__full_name")
    ordering = ("-created_at",)
    autocomplete_fields = ("order", "product_party", "roll", "warehouse")
