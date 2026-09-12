from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import User


@admin.register(User)
class UserAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "full_name",
        "phone_number",
        "role",
        "employee",
        "is_staff",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_superuser",
        "is_active",
        "role",
        "employee__branch",
        "is_staff",
        "created_at",
    )
    search_fields = ("full_name", "phone_number", "role__name", "employee__full_name")
    ordering = ("-created_at",)
    autocomplete_fields = ("role", "employee")
