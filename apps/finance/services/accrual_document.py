from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.hr.models import Employee
from apps.hr.services import annotate_employee_status

from ..models import AccrualRetentionDocument


def ensure_draft(document):
    """Hujjat faqat qoralama holatda tahrirlanishi mumkinligini tekshiradi."""
    if document.status != AccrualRetentionDocument.Status.DRAFT:
        raise ValidationError(
            f"Hujjat «{document.get_status_display()}» holatida — "
            "uni o'zgartirib bo'lmaydi."
        )


def ensure_employees_employed(employees):
    """Xodimlarning hammasi hozir ishlab turganini tekshiradi (bitta so'rov bilan).

    Ishdan bo'shatilgan yoki ishga olinmagan xodimga hujjat belgilab bo'lmaydi.
    """
    ids = [employee.pk for employee in employees]
    employed_ids = set(
        annotate_employee_status(Employee.objects.filter(pk__in=ids))
        .filter(is_employed=True)
        .values_list("pk", flat=True)
    )
    inactive = [e.full_name for e in employees if e.pk not in employed_ids]
    if inactive:
        raise ValidationError(
            {
                "employee": "Ishdan bo'shatilgan yoki ishga olinmagan xodimga "
                f"hujjat belgilab bo'lmaydi: {', '.join(inactive)}."
            }
        )


@transaction.atomic
def approve_document(document):
    """Qoralama hujjatni tasdiqlaydi."""
    document = AccrualRetentionDocument.objects.select_for_update().get(pk=document.pk)
    if document.status != AccrualRetentionDocument.Status.DRAFT:
        raise ValidationError("Faqat qoralama hujjatni tasdiqlash mumkin.")
    document.status = AccrualRetentionDocument.Status.APPROVED
    document.save(update_fields=["status", "updated_at"])
    return document


@transaction.atomic
def cancel_document(document):
    """Qoralama yoki tasdiqlangan hujjatni bekor qiladi."""
    document = AccrualRetentionDocument.objects.select_for_update().get(pk=document.pk)
    if document.status == AccrualRetentionDocument.Status.CANCELLED:
        raise ValidationError("Hujjat allaqachon bekor qilingan.")
    document.status = AccrualRetentionDocument.Status.CANCELLED
    document.save(update_fields=["status", "updated_at"])
    return document
