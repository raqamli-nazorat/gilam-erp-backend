import datetime

from django.db.models import Exists, OuterRef, Q, Subquery

from ..models import RecruitmentDismissal


def _has_active_branch_subquery(employee_field="pk"):
    """Xodim ixtiyoriy bitta filialda hozir ishlab turganini tekshiruvchi subquery (N+1 siz).

    Filial bo'yicha oxirgi voqea "ishga olish" bo'lib, undan keyin o'sha filialda
    "bo'shatish" bo'lmagan bo'lsa — o'sha filial hisobida xodim hali ham faol.
    Sana bir xil bo'lsa (bir kunda bo'shatib, qayta ishga olingan bo'lsa) —
    `created_at` bo'yicha aniqlanadi, kim chinakam keyinroq bo'lganligi.
    """
    later_dismissal = RecruitmentDismissal.objects.filter(
        Q(rec_dism_date__gt=OuterRef("rec_dism_date"))
        | Q(
            rec_dism_date=OuterRef("rec_dism_date"),
            created_at__gte=OuterRef("created_at"),
        ),
        employee_id=OuterRef("employee_id"),
        branch_id=OuterRef("branch_id"),
        type=RecruitmentDismissal.Type.DISMISSAL,
        is_active=True,
    )
    active_recruitments = RecruitmentDismissal.objects.filter(
        employee_id=OuterRef(employee_field),
        type=RecruitmentDismissal.Type.RECRUITMENT,
        is_active=True,
    ).exclude(Exists(later_dismissal))
    return Exists(active_recruitments)


def annotate_employee_status(queryset, employee_field="pk"):
    """Xodim queryset'iga joriy ish holati va oxirgi voqea ma'lumotlarini N+1 siz qo'shadi."""
    latest_rd = RecruitmentDismissal.objects.filter(
        employee_id=OuterRef(employee_field), is_active=True
    ).order_by("-rec_dism_date", "-created_at")

    return queryset.annotate(
        is_employed=_has_active_branch_subquery(employee_field),
        latest_status_type=Subquery(latest_rd.values("type")[:1]),
        latest_status_date=Subquery(latest_rd.values("rec_dism_date")[:1]),
        latest_status_reason=Subquery(latest_rd.values("dismissal_reason")[:1]),
    )


def annotate_latest_position(queryset, employee_field="pk"):
    """Xodim queryset'iga oxirgi faol ishga olish yozuvidagi lavozim nomini N+1 siz qo'shadi."""
    latest_recruitment = RecruitmentDismissal.objects.filter(
        employee_id=OuterRef(employee_field),
        type=RecruitmentDismissal.Type.RECRUITMENT,
        is_active=True,
    ).order_by("-rec_dism_date", "-created_at")

    return queryset.annotate(
        latest_position_name=Subquery(latest_recruitment.values("position__name")[:1])
    )


def build_employment_status(
    is_employed, latest_status_type, latest_status_date, latest_status_reason
):
    """Annotatsiyadagi qiymatlardan frontend uchun status obyektini yasaydi."""
    if is_employed:
        return {
            "status": "active",
            "label": "Faol",
            "date": latest_status_date,
            "reason": "",
        }
    if latest_status_type is not None:
        return {
            "status": "dismissed",
            "label": "Ishdan chiqarilgan",
            "date": latest_status_date,
            "reason": latest_status_reason or "",
        }
    return {
        "status": "not_hired",
        "label": "Ishga olinmagan",
        "date": None,
        "reason": "",
    }


def get_employee_status_counts(queryset):
    """`annotate_employee_status` bilan ishlangan queryset uchun {total, active, inactive} sonlarini hisoblaydi."""
    total = queryset.count()
    active = queryset.filter(is_employed=True).count()
    return {"total": total, "active": active, "inactive": total - active}


def get_active_recruitment_records(employee):
    """Xodimning hozir faol (hali bo'shatilmagan) ishga olish yozuvlarini qaytaradi.

    Har filial bo'yicha eng oxirgi voqea "ishga olish" bo'lsa — o'sha yozuv
    faol hisoblanadi (`dismiss/` endpointida branch/position/card_number/salary_type
    shu yozuvdan ko'chiriladi).
    """
    records = (
        RecruitmentDismissal.objects.filter(employee=employee, is_active=True)
        .select_related("branch", "position")
        .order_by("branch_id", "-rec_dism_date", "-created_at")
    )

    latest_by_branch = {}
    for record in records:
        latest_by_branch.setdefault(record.branch_id, record)

    return [
        record
        for record in latest_by_branch.values()
        if record.type == RecruitmentDismissal.Type.RECRUITMENT
    ]


def get_employee_employment_history(employee):
    """Xodimning har bir filial bo'yicha ish tarixini (joriy holati bilan) qaytaradi.

    Har bir filial uchun oxirgi "ishga olish" yozuvidagi lavozim va sana ko'rsatiladi;
    o'sha sanadan keyin o'sha filialda "bo'shatish" bo'lgan bo'lsa — Nofaol, bo'lmasa Faol.
    """
    records = (
        RecruitmentDismissal.objects.filter(employee=employee, is_active=True)
        .select_related("branch", "branch__organization", "position")
        .order_by("branch_id", "-rec_dism_date", "-created_at")
    )

    history_by_branch = {}
    for record in records:
        entry = history_by_branch.setdefault(
            record.branch_id,
            {
                "organization": record.branch.organization,
                "branch": record.branch,
                "position": None,
                "hired_at": None,
                "is_employed": False,
                "_hired_key": None,
                "_dismissal_keys": [],
            },
        )
        key = (record.rec_dism_date, record.created_at)
        if (
            record.type == RecruitmentDismissal.Type.RECRUITMENT
            and entry["hired_at"] is None
        ):
            entry["position"] = record.position
            entry["hired_at"] = record.rec_dism_date
            entry["_hired_key"] = key
        elif record.type == RecruitmentDismissal.Type.DISMISSAL:
            entry["_dismissal_keys"].append(key)

    result = []
    for entry in history_by_branch.values():
        hired_key = entry["_hired_key"]
        dismissed_after = hired_key is not None and any(
            key >= hired_key for key in entry["_dismissal_keys"]
        )
        entry["is_employed"] = hired_key is not None and not dismissed_after
        del entry["_hired_key"]
        del entry["_dismissal_keys"]
        result.append(entry)

    result.sort(key=lambda e: e["hired_at"] or datetime.date.min, reverse=True)
    return result
