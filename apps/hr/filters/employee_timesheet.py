import django_filters

from ..models import EmployeeTimesheet, EmployeeTimesheetItem


class EmployeeTimesheetFilter(django_filters.FilterSet):
    branch = django_filters.UUIDFilter(field_name="branch_id")
    for_month = django_filters.ChoiceFilter(choices=EmployeeTimesheet.Month.choices)
    status = django_filters.ChoiceFilter(choices=EmployeeTimesheet.Status.choices)
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = EmployeeTimesheet
        fields = ["branch", "for_month", "status", "start_date", "end_date"]


class EmployeeTimesheetItemFilter(django_filters.FilterSet):
    employee_timesheet = django_filters.UUIDFilter(field_name="employee_timesheet_id")
    employee = django_filters.UUIDFilter(field_name="employee_id")
    date_from = django_filters.DateFilter(
        field_name="date", lookup_expr="date__gte", label="Sana (dan)"
    )
    date_to = django_filters.DateFilter(
        field_name="date", lookup_expr="date__lte", label="Sana (gacha)"
    )

    class Meta:
        model = EmployeeTimesheetItem
        fields = ["employee_timesheet", "employee", "date_from", "date_to"]
