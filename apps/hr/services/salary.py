from collections import defaultdict
from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.finance.models import AccrualRetention, AccrualRetentionDocument, Currency
from apps.finance.services.currency import get_rate

from ..models import (
    CalculatingSalary,
    EmployeeTimesheet,
    EmployeeTimesheetItem,
    RecruitmentDismissal,
)

CENT = Decimal("0.01")


def ensure_draft(salary):
    """Oylik faqat qoralama holatda tahrirlanishi mumkinligini tekshiradi."""
    if salary.status != CalculatingSalary.Status.DRAFT:
        raise ValidationError(
            f"Oylik «{salary.get_status_display()}» holatida — "
            "uni o'zgartirib bo'lmaydi."
        )


def _approved_exists(employee_id, for_month, year, exclude_pk=None):
    """Xodimning shu oyda (yaratilgan yil bo'yicha) tasdiqlangan oyligi bormi.

    Modelda yil maydoni yo'q, shuning uchun yil `created_at` orqali aniqlanadi.
    """
    queryset = CalculatingSalary.objects.active().filter(
        employee_id=employee_id,
        for_month=for_month,
        status=CalculatingSalary.Status.APPROVED,
        created_at__year=year,
    )
    if exclude_pk is not None:
        queryset = queryset.exclude(pk=exclude_pk)
    return queryset.exists()


@transaction.atomic
def approve_salary(salary):
    """Qoralama oylikni tasdiqlaydi (bir xodimga bir oyda bitta tasdiqlangan)."""
    salary = CalculatingSalary.objects.select_for_update().get(pk=salary.pk)
    if salary.status != CalculatingSalary.Status.DRAFT:
        raise ValidationError("Faqat qoralama oylikni tasdiqlash mumkin.")
    if _approved_exists(
        salary.employee_id, salary.for_month, salary.created_at.year, salary.pk
    ):
        raise ValidationError(
            "Bu xodim uchun shu oyda tasdiqlangan oylik allaqachon mavjud."
        )
    salary.status = CalculatingSalary.Status.APPROVED
    salary.save(update_fields=["status", "updated_at"])
    return salary


@transaction.atomic
def cancel_salary(salary):
    """Qoralama yoki tasdiqlangan oylikni bekor qiladi."""
    salary = CalculatingSalary.objects.select_for_update().get(pk=salary.pk)
    if salary.status == CalculatingSalary.Status.CANCELLED:
        raise ValidationError("Oylik allaqachon bekor qilingan.")
    salary.status = CalculatingSalary.Status.CANCELLED
    salary.save(update_fields=["status", "updated_at"])
    return salary


def _employed_records(branch):
    """Filialda hozir ishlab turgan xodimlarning oxirgi (ishga olish) yozuvlari."""
    records = (
        RecruitmentDismissal.objects.filter(
            branch=branch,
            status=RecruitmentDismissal.Status.APPROVED,
            is_active=True,
        )
        .select_related("employee")
        .order_by("employee_id", "-rec_dism_date", "-created_at")
    )
    latest = {}
    for record in records:
        latest.setdefault(record.employee_id, record)
    return [
        record
        for record in latest.values()
        if record.type == RecruitmentDismissal.Type.RECRUITMENT
    ]


def _hours_by_employee(branch, month, year, employee_ids):
    """Tasdiqlangan tabellardan xodim bo'yicha rejadagi va haqiqiy soatlar yig'indisi."""
    rows = (
        EmployeeTimesheetItem.objects.active()
        .filter(
            employee_timesheet__branch=branch,
            employee_timesheet__status=EmployeeTimesheet.Status.APPROVED,
            employee_timesheet__is_active=True,
            date__year=year,
            date__month=month,
            employee_id__in=employee_ids,
        )
        .values("employee_id")
        .annotate(plan=Sum("work_hour_in_plan"), fact=Sum("work_hour_in_fact"))
    )
    return {row["employee_id"]: row for row in rows}


def _documents_by_employee(branch, month, year, employee_ids):
    """Oydagi tasdiqlangan hisoblash / ushlab qolish hujjatlarini xodim bo'yicha guruhlaydi."""
    documents = (
        AccrualRetentionDocument.objects.active()
        .filter(
            branch=branch,
            status=AccrualRetentionDocument.Status.APPROVED,
            date__year=year,
            date__month=month,
            employee_id__in=employee_ids,
        )
        .select_related("accrual_retention", "accrual_retention__currency")
    )
    grouped = defaultdict(list)
    for document in documents:
        grouped[document.employee_id].append(document)
    return grouped


def _adjustments_total(documents, base, rates):
    """Hujjatlar bo'yicha qo'shimchalar (+) va ushlanmalar (−) yig'indisini UZS da hisoblaydi."""
    total = Decimal(0)
    for document in documents:
        accrual = document.accrual_retention
        if accrual.type == AccrualRetention.Type.PERCENT:
            amount = base * accrual.value / Decimal(100)
        else:
            day = timezone.localtime(document.date).date()
            key = (accrual.currency_id, day)
            if key not in rates:
                rates[key] = get_rate(accrual.currency, day)
            amount = accrual.value * rates[key]
        total += -amount if accrual.is_retention else amount
    return total


def _compute_amount(record, hours, documents, rates):
    """Xodim oyligini (UZS) hisoblaydi yoki o'tkazib yuborish sababini qaytaradi."""
    if record.salary_type != RecruitmentDismissal.SalaryType.FIXED_AMOUNT:
        return None, (
            f"Oylik turi «{record.get_salary_type_display()}» hisoblanmaydi "
            "(faqat belgilangan summa)."
        )
    if not record.fix_summa:
        return None, "Belgilangan summa kiritilmagan."
    if hours is None or not hours["plan"]:
        return None, "Tabelda rejadagi ish soati yo'q."
    ratio = min((hours["fact"] or Decimal(0)) / hours["plan"], Decimal(1))
    base = (record.fix_summa * ratio).quantize(CENT, rounding=ROUND_HALF_UP)
    total = base + _adjustments_total(documents, base, rates)
    return max(total, Decimal(0)).quantize(CENT, rounding=ROUND_HALF_UP), None


@transaction.atomic
def calculate_salaries(branch, month, year):
    """Filial va oy bo'yicha ishlayotgan xodimlar oyligini hisoblab, qoralama qatorlarini yaratadi.

    Formula: belgilangan summa × (haqiqiy soat / rejadagi soat, ko'pi bilan 1) ±
    tasdiqlangan hujjatlar (foiz — asosiy oylikdan, summa — hujjat sanasi kursi bilan).
    Mavjud qoralama yangilanadi, tasdiqlangan oylik bor xodim o'tkazib yuboriladi.
    """
    uzs = Currency.objects.active().filter(short_name="UZS").first()
    if uzs is None:
        raise ValidationError({"currency": "UZS valyutasi ma'lumotnomada topilmadi."})
    if (
        not EmployeeTimesheet.objects.active()
        .filter(
            branch=branch, for_month=month, status=EmployeeTimesheet.Status.APPROVED
        )
        .exists()
    ):
        raise ValidationError(
            {"for_month": "Bu filial va oy uchun tasdiqlangan tabel yo'q."}
        )

    records = _employed_records(branch)
    ids = [record.employee_id for record in records]
    hours = _hours_by_employee(branch, month, year, ids)
    documents = _documents_by_employee(branch, month, year, ids)
    existing = {
        salary.employee_id: salary
        for salary in CalculatingSalary.objects.active()
        .filter(
            branch=branch,
            for_month=month,
            employee_id__in=ids,
            created_at__year=timezone.localdate().year,
        )
        .exclude(status=CalculatingSalary.Status.CANCELLED)
        .order_by("-created_at")
    }

    rates, salaries, skipped = {}, [], []
    for record in records:
        employee = record.employee
        current = existing.get(employee.pk)
        if current and current.status == CalculatingSalary.Status.APPROVED:
            skipped.append(
                {
                    "employee": employee.pk,
                    "full_name": employee.full_name,
                    "reason": "Tasdiqlangan oylik allaqachon mavjud.",
                }
            )
            continue
        amount, reason = _compute_amount(
            record, hours.get(employee.pk), documents[employee.pk], rates
        )
        if reason:
            skipped.append(
                {
                    "employee": employee.pk,
                    "full_name": employee.full_name,
                    "reason": reason,
                }
            )
            continue
        if current:
            current.amount = current.currency_amount = amount
            current.currency = uzs
            current.save(
                update_fields=["amount", "currency", "currency_amount", "updated_at"]
            )
            salaries.append(current)
        else:
            salaries.append(
                CalculatingSalary.objects.create(
                    branch=branch,
                    employee=employee,
                    for_month=month,
                    amount=amount,
                    currency=uzs,
                    currency_amount=amount,
                )
            )
    return salaries, skipped
