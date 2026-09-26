from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import RecruitmentDismissal


@admin.register(RecruitmentDismissal)
class RecruitmentDismissalAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "type",
        "status",
        "branch",
        "employee",
        "position",
        "card_number",
        "card_image",
        "salary_type",
        "fix_summa",
        "fix_percent",
        "rec_dism_date",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_active",
        "type",
        "status",
        "branch",
        "position",
        "salary_type",
        "created_at",
    )
    search_fields = (
        "card_number",
        "card_image",
        "dismissal_reason",
        "branch__name",
        "employee__phone_number",
        "employee__full_name",
        "position__name",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("branch", "employee", "position")

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = list(super().get_readonly_fields(request, obj))
        if obj and obj.status != RecruitmentDismissal.Status.DRAFT:
            readonly_fields.append("status")
        return readonly_fields
