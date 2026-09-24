from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import ProductStock


@admin.register(ProductStock)
class ProductStockAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "warehouse",
        "product_party",
        "quantity",
        "total_length_meters",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "warehouse", "created_at")
    search_fields = ("warehouse__name", "product_party__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("warehouse", "product_party")
