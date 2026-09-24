import django_filters

from apps.base.filters import UUIDInFilter

from ..models import InstallmentSchedule


class InstallmentScheduleFilter(django_filters.FilterSet):
    agreement = UUIDInFilter(field_name="agreement_id", lookup_expr="in")
    status = django_filters.ChoiceFilter(choices=InstallmentSchedule.Status.choices)
    due_date = django_filters.DateFilter()
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = InstallmentSchedule
        fields = ["agreement", "status", "due_date", "start_date", "end_date"]
