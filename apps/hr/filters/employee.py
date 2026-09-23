import django_filters
from django.db.models import Q

from apps.base.filters import CharInFilter

from ..models import Employee, RecruitmentDismissal


class EmployeeFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(lookup_expr="icontains")
    phone_number = django_filters.CharFilter(lookup_expr="icontains")
    passport_seria = django_filters.CharFilter(lookup_expr="icontains")
    passport_number = django_filters.CharFilter(lookup_expr="icontains")
    jsshr = django_filters.CharFilter(lookup_expr="icontains")
    stir = django_filters.CharFilter(lookup_expr="icontains")
    organization = django_filters.UUIDFilter(field_name="organization_id")
    branch = django_filters.UUIDFilter(field_name="branch_id")
    region = django_filters.UUIDFilter(field_name="region_id")
    district = django_filters.UUIDFilter(field_name="district_id")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )
    is_active = django_filters.BooleanFilter(
        field_name="is_employed", label="Holat (Faol/Nofaol)"
    )
    employment_status = CharInFilter(
        method="filter_employment_status",
        label="Ish holati: not_hired, dismissed, active (vergul bilan bir nechta)",
    )

    def filter_employment_status(self, queryset, name, value):
        """`not_hired`/`dismissed`/`active` qiymatlari bo'yicha xodimlarni filtrlaydi.

        `not_hired` — hech qachon ishga olinmagan, `dismissed` — oldin ishlagan,
        keyin bo'shagan, `active` — hozir faol ishlaydi. Bir nechtasi vergul bilan
        birga so'ralishi mumkin, masalan `?employment_status=not_hired,dismissed`.
        """
        q = Q()
        if "active" in value:
            q |= Q(is_employed=True)
        if "dismissed" in value:
            q |= Q(
                is_employed=False,
                latest_status_type=RecruitmentDismissal.Type.DISMISSAL,
            )
        if "not_hired" in value:
            q |= Q(is_employed=False, latest_status_type__isnull=True)
        return queryset.filter(q) if q else queryset

    class Meta:
        model = Employee
        fields = [
            "full_name",
            "phone_number",
            "passport_seria",
            "passport_number",
            "jsshr",
            "stir",
            "organization",
            "branch",
            "region",
            "district",
            "start_date",
            "end_date",
            "is_active",
            "employment_status",
        ]
