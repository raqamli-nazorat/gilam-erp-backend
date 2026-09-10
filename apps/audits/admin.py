"""
Audit loglari uchun Django Admin integratsiyasi.

Ushbu modul auditlog LogEntry modelini Unfold Admin uslubida
admin panelga ro'yxatdan o'tkazadi.
"""

from auditlog.admin import LogEntryAdmin
from auditlog.models import LogEntry
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from unfold.admin import ModelAdmin

try:
    admin.site.unregister(LogEntry)
except NotRegistered:
    pass


@admin.register(LogEntry)
class UnfoldLogEntryAdmin(ModelAdmin, LogEntryAdmin):
    """
    LogEntry uchun Unfold mavzusidagi Admin klassi.
    """

    list_display = ["created", "resource_url", "action", "msg_short", "user_url"]
    list_filter = ["action"]
    search_fields = [
        "timestamp",
        "object_repr",
        "changes",
        "actor__first_name",
        "actor__last_name",
    ]
