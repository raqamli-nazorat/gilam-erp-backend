from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import InstallmentSchedule


@admin.register(InstallmentSchedule)
class InstallmentScheduleAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "agreement",
        "payment_number",
        "due_date",
        "amount_to_pay",
        "paid_amount",
        "status",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "status", "created_at")
    search_fields = ("agreement__agreement_number",)
    ordering = ("-created_at",)
    autocomplete_fields = ("agreement",)
