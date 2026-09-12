from django.contrib import admin

from apps.base.admin import BaseModelAdmin

from ..models import Counterparty


@admin.register(Counterparty)
class CounterpartyAdmin(BaseModelAdmin):
    list_display = ("id", "name", "phone_number", "type", "is_active", "created_at")
    list_filter = ("is_active", "type", "created_at")
    search_fields = ("name", "phone_number", "type__name")
    ordering = ("-created_at",)
    autocomplete_fields = ("type",)
