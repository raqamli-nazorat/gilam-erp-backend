from django.db import transaction
from rest_framework.exceptions import ValidationError

from ..models import EmployeeTimesheet


def lock_error_message(timesheet):
    """Tabel qulflangan (qoralama emas) bo'lsa, xabar matnini qaytaradi."""
    return (
        f"Tabel «{timesheet.get_status_display()}» holatida — "
        "uni o'zgartirib bo'lmaydi."
    )


def ensure_draft(timesheet):
    """Tabel faqat qoralama holatda tahrirlanishi mumkinligini tekshiradi."""
    if timesheet.status != EmployeeTimesheet.Status.DRAFT:
        raise ValidationError(lock_error_message(timesheet))


@transaction.atomic
def approve_timesheet(timesheet):
    """Qoralama tabelni tasdiqlaydi."""
    timesheet = EmployeeTimesheet.objects.select_for_update().get(pk=timesheet.pk)
    if timesheet.status != EmployeeTimesheet.Status.DRAFT:
        raise ValidationError("Faqat qoralama tabelni tasdiqlash mumkin.")
    timesheet.status = EmployeeTimesheet.Status.APPROVED
    timesheet.save(update_fields=["status", "updated_at"])
    return timesheet


@transaction.atomic
def cancel_timesheet(timesheet):
    """Qoralama yoki tasdiqlangan tabelni bekor qiladi."""
    timesheet = EmployeeTimesheet.objects.select_for_update().get(pk=timesheet.pk)
    if timesheet.status == EmployeeTimesheet.Status.CANCELLED:
        raise ValidationError("Tabel allaqachon bekor qilingan.")
    timesheet.status = EmployeeTimesheet.Status.CANCELLED
    timesheet.save(update_fields=["status", "updated_at"])
    return timesheet
