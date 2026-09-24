from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import InstallmentAgreement


@admin.register(InstallmentAgreement)
class InstallmentAgreementAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "agreement_number",
        "organization",
        "customer",
        "order",
        "total_amount",
        "remaining_amount",
        "status",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "status", "organization", "created_at")
    search_fields = ("agreement_number", "customer__full_name", "organization__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("organization", "order", "customer")
