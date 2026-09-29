from django.db import transaction
from rest_framework.exceptions import ValidationError

from ..models import CalculatingSalary, EmployeeTimesheet, EmployeeTimesheetItem


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


def ensure_no_approved_salaries(timesheet):
    """Tabel oyi uchun tasdiqlangan oylik bo'lsa, tabelni bekor qilishni taqiqlaydi.

    Oylikda yil maydoni yo'q, shuning uchun yil `created_at` orqali olinadi;
    dekabr oyligi odatda keyingi yilda hisoblanadi, shu sababli u ham hisobga olinadi.
    """
    years = [timesheet.year]
    if timesheet.for_month == EmployeeTimesheet.Month.DECEMBER:
        years.append(timesheet.year + 1)
    approved = CalculatingSalary.objects.active().filter(
        branch_id=timesheet.branch_id,
        for_month=timesheet.for_month,
        status=CalculatingSalary.Status.APPROVED,
        created_at__year__in=years,
    )
    if approved.exists():
        raise ValidationError(
            "Bu filial va oy uchun tasdiqlangan oyliklar bor. "
            "Tabelni bekor qilishdan oldin ularni bekor qiling."
        )


@transaction.atomic
def approve_timesheet(timesheet):
    """Qoralama tabelni tasdiqlaydi."""
    timesheet = EmployeeTimesheet.objects.select_for_update().get(pk=timesheet.pk)
    if timesheet.status != EmployeeTimesheet.Status.DRAFT:
        raise ValidationError("Faqat qoralama tabelni tasdiqlash mumkin.")
    has_plan_hours = EmployeeTimesheetItem.objects.active().filter(
        employee_timesheet=timesheet, work_hour_in_plan__gt=0
    )
    if not has_plan_hours.exists():
        raise ValidationError(
            "Tabelda rejadagi ish soati kiritilgan qator yo'q. "
            "Tasdiqlashdan oldin tabelni to'ldiring."
        )
    timesheet.status = EmployeeTimesheet.Status.APPROVED
    timesheet.save(update_fields=["status", "updated_at"])
    return timesheet


@transaction.atomic
def cancel_timesheet(timesheet):
    """Qoralama yoki tasdiqlangan tabelni bekor qiladi."""
    timesheet = EmployeeTimesheet.objects.select_for_update().get(pk=timesheet.pk)
    if timesheet.status == EmployeeTimesheet.Status.CANCELLED:
        raise ValidationError("Tabel allaqachon bekor qilingan.")
    if timesheet.status == EmployeeTimesheet.Status.APPROVED:
        ensure_no_approved_salaries(timesheet)
    timesheet.status = EmployeeTimesheet.Status.CANCELLED
    timesheet.save(update_fields=["status", "updated_at"])
    return timesheet
