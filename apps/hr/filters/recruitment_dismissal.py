import django_filters

from ..models import RecruitmentDismissal


class RecruitmentDismissalFilter(django_filters.FilterSet):
    type = django_filters.ChoiceFilter(choices=RecruitmentDismissal.Type.choices)
    salary_type = django_filters.ChoiceFilter(
        choices=RecruitmentDismissal.SalaryType.choices
    )
    branch = django_filters.UUIDFilter(field_name="branch_id")
    employee = django_filters.UUIDFilter(field_name="employee_id")
    position = django_filters.UUIDFilter(field_name="position_id")
    card_number = django_filters.CharFilter(lookup_expr="icontains")
    rec_dism_date = django_filters.DateFilter()
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = RecruitmentDismissal
        fields = [
            "type",
            "salary_type",
            "branch",
            "employee",
            "position",
            "card_number",
            "rec_dism_date",
            "start_date",
            "end_date",
        ]
