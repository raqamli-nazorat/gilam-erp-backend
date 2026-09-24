from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import Order


@admin.register(Order)
class OrderAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "organization",
        "branch",
        "customer",
        "seller",
        "final_amount",
        "payment_status",
        "order_status",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_active",
        "organization",
        "branch",
        "payment_status",
        "order_status",
        "created_at",
    )
    search_fields = (
        "customer__full_name",
        "seller__full_name",
        "branch__name",
        "organization__name",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("organization", "branch", "customer", "seller", "cashier")
