from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import StockTransaction


@admin.register(StockTransaction)
class StockTransactionAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "transaction_type",
        "product_party",
        "from_warehouse",
        "to_warehouse",
        "ref_type",
        "created_at",
    )
    list_filter = ("transaction_type", "ref_type", "is_active", "created_at")
    search_fields = ("product_party__name", "roll__roll_number")
    ordering = ("-created_at",)
    autocomplete_fields = (
        "organization",
        "product_party",
        "roll",
        "from_warehouse",
        "to_warehouse",
    )
