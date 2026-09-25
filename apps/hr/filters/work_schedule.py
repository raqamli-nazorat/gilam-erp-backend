import django_filters

from ..models import WorkSchedule, WorkScheduleItem


class WorkScheduleFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )
    updated_start_date = django_filters.DateFilter(
        field_name="updated_at", lookup_expr="gte", label="O'zgartirilgan sana (dan)"
    )
    updated_end_date = django_filters.DateFilter(
        field_name="updated_at", lookup_expr="lte", label="O'zgartirilgan sana (gacha)"
    )

    class Meta:
        model = WorkSchedule
        fields = [
            "branch",
            "name",
            "is_active",
            "start_date",
            "end_date",
            "updated_start_date",
            "updated_end_date",
        ]


class WorkScheduleItemFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    is_active = django_filters.BooleanFilter(field_name="is_active")
    day_date_from = django_filters.DateFilter(
        field_name="day_date", lookup_expr="gte", label="Sana (dan)"
    )
    day_date_to = django_filters.DateFilter(
        field_name="day_date", lookup_expr="lte", label="Sana (gacha)"
    )

    class Meta:
        model = WorkScheduleItem
        fields = [
            "work_schedule",
            "day_type",
            "name",
            "is_active",
            "day_date_from",
            "day_date_to",
        ]
