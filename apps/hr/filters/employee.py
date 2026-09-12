import django_filters

from ..models import Employee


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
        ]
