from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import AccrualRetentionDocument


@admin.register(AccrualRetentionDocument)
class AccrualRetentionDocumentAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "branch",
        "employee",
        "accrual_retention",
        "date",
        "status",
        "is_active",
    )
    list_filter = ("is_active", "status", "branch", "accrual_retention")
    search_fields = ("employee__full_name", "accrual_retention__name")
    ordering = ("-date",)
    autocomplete_fields = ("branch", "employee", "accrual_retention")
