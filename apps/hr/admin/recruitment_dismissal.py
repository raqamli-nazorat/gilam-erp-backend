from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import RecruitmentDismissal


@admin.register(RecruitmentDismissal)
class RecruitmentDismissalAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "type",
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
