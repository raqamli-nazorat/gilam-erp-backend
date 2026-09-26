import django_filters

from ..models import AccrualRetentionDocument


class AccrualRetentionDocumentFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    employee = django_filters.UUIDFilter(field_name="employee_id")
    accrual_retention = django_filters.UUIDFilter(field_name="accrual_retention_id")
    is_retention = django_filters.BooleanFilter(
        field_name="accrual_retention__is_retention",
        label="Ushlab qolish (true) / hisoblash (false)",
    )
    status = django_filters.ChoiceFilter(
        choices=AccrualRetentionDocument.Status.choices
    )
    date_from = django_filters.DateFilter(
        field_name="date", lookup_expr="date__gte", label="Sana (dan)"
    )
    date_to = django_filters.DateFilter(
        field_name="date", lookup_expr="date__lte", label="Sana (gacha)"
    )

    class Meta:
        model = AccrualRetentionDocument
        fields = [
            "branch",
            "employee",
            "accrual_retention",
            "is_retention",
            "status",
            "date_from",
            "date_to",
        ]
