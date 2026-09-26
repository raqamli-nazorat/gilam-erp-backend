import django_filters

from ..models import CalculatingSalary


class CalculatingSalaryFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    employee = django_filters.UUIDFilter(field_name="employee_id")
    currency = django_filters.UUIDFilter(field_name="currency_id")
    for_month = django_filters.ChoiceFilter(choices=CalculatingSalary.Month.choices)
    status = django_filters.ChoiceFilter(choices=CalculatingSalary.Status.choices)
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = CalculatingSalary
        fields = [
            "branch",
            "employee",
            "currency",
            "for_month",
            "status",
            "start_date",
            "end_date",
        ]
