from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import Payment


@admin.register(Payment)
class PaymentAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "organization",
        "customer",
        "order",
        "amount",
        "payment_method",
        "payment_type",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_active",
        "payment_method",
        "payment_type",
        "organization",
        "created_at",
    )
    search_fields = ("customer__full_name", "organization__name")
    ordering = ("-created_at",)
    autocomplete_fields = (
        "organization",
        "order",
        "installment_agreement",
        "customer",
    )
