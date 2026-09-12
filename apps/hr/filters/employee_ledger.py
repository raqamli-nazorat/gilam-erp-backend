import django_filters

from ..models import EmployeeLedger


class EmployeeLedgerFilter(django_filters.FilterSet):
    type = django_filters.ChoiceFilter(choices=EmployeeLedger.Type.choices)
    branch = django_filters.UUIDFilter(field_name="branch_id")
    employee = django_filters.UUIDFilter(field_name="employee_id")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = EmployeeLedger
        fields = ["type", "branch", "employee", "start_date", "end_date"]
