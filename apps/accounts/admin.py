from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from .models import (
    Role,
    User,
)


@admin.register(Role)
class RoleAdmin(BaseModelAdmin):
    list_display = ("id", "name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name",)
    ordering = ("-created_at",)


@admin.register(User)
class UserAdmin(BaseModelAdmin):
    list_display = (
        "id",
        "full_name",
        "phone_number",
        "role",
        "branch",
        "is_staff",
        "is_active",
        "created_at",
    )
    list_filter = (
        "is_superuser",
        "is_active",
        "role",
        "branch",
        "is_staff",
        "created_at",
    )
    search_fields = ("full_name", "phone_number", "role__name", "branch__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("role", "branch")
