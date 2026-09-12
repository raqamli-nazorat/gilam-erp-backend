from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import Employee


@admin.register(Employee)
class EmployeeAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "branch",
        "full_name",
        "region",
        "district",
        "address",
        "passport_seria",
        "passport_number",
        "jsshr",
        "stir",
        "phone_number",
        "is_active",
        "created_at",
    )
    list_filter = ("is_active", "branch", "region", "district", "created_at")
    search_fields = (
        "full_name",
        "address",
        "passport_seria",
        "passport_number",
        "jsshr",
        "stir",
        "phone_number",
        "description",
        "branch__name",
        "region__name",
    )
    ordering = ("-created_at",)
    autocomplete_fields = ("branch", "region", "district")
