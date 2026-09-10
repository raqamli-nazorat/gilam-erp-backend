"""
Django Admin paneli uchun bazaviy ModelAdmin klassi.

Ushbu modul Unfold admin mavzusiga moslashgan hamda soft-delete
va hard-delete operatsiyalarini qo'llab-quvvatlaydigan BaseModelAdmin klassini taqdim etadi.
"""

from django.contrib import admin
from unfold.admin import ModelAdmin

from .exports import ExportExcelMixin


class BaseModelAdmin(ExportExcelMixin, ModelAdmin):
    """
    Loyihadagi barcha modellar uchun admin paneli bazaviy klassi.

    Standart o'chirish harakatlarida Soft Delete qo'llaydi,
    shuningdek obyektlarni bazadan butunlay o'chirish uchun action beradi.
    """

    def delete_model(self, request, obj):
        """Yagona obyekt o'chirilganda soft delete bajaradi."""
        obj.delete()

    def delete_queryset(self, request, queryset):
        """Tanlangan obyektlar to'plami o'chirilganda soft delete bajaradi."""
        queryset.delete()

    actions = ["really_hard_delete"]

    @admin.action(description="Butunlay o'chirish")
    def really_hard_delete(self, request, queryset):
        """
        Tanlangan obyektlarni ma'lumotlar bazasidan butunlay o'chirib tashlash harakati (Hard Delete).
        """
        count = queryset.count()

        if hasattr(queryset, "hard_delete"):
            queryset.hard_delete()
        else:
            queryset.delete()

        self.message_user(
            request,
            f"Muvaffaqiyatli: {count} ta obyekt bazadan butunlay o'chirib yuborildi.",
        )
