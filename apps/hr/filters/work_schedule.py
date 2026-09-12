import django_filters

from ..models import WorkSchedule


class WorkScheduleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    branch = django_filters.UUIDFilter(field_name="branch_id")
    from_date = django_filters.DateFilter(lookup_expr="gte")
    to_date = django_filters.DateFilter(lookup_expr="lte")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = WorkSchedule
        fields = ["name", "branch", "from_date", "to_date", "start_date", "end_date"]
