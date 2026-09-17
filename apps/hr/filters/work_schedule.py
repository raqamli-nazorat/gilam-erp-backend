import django_filters

from ..models import WorkSchedule


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
            "name",
            "is_active",
            "start_date",
            "end_date",
            "updated_start_date",
            "updated_end_date",
        ]
