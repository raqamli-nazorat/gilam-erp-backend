"""
Organization app ViewSet'lari uchun FilterSet klasslari.

FK maydonlar `UUIDInFilter` orqali vergul bilan ajratilgan ro'yxatni,
nomlar esa `icontains` bo'yicha qidiruvni qo'llab-quvvatlaydi.
"""

import django_filters

from apps.base.filters import UUIDInFilter

from .models import Branch, Country, District, Organization, Region


class CountryFilter(django_filters.FilterSet):
    """Davlatlarni nomi bo'yicha filtrlaydi."""

    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Country
        fields = ["name"]


class RegionFilter(django_filters.FilterSet):
    """Viloyatlarni nomi va davlati bo'yicha filtrlaydi."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    country = UUIDInFilter(field_name="country_id", lookup_expr="in")

    class Meta:
        model = Region
        fields = ["name", "country"]


class DistrictFilter(django_filters.FilterSet):
    """Tumanlarni nomi va viloyati bo'yicha filtrlaydi."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    region = UUIDInFilter(field_name="region_id", lookup_expr="in")

    class Meta:
        model = District
        fields = ["name", "region"]


class OrganizationFilter(django_filters.FilterSet):
    """Tashkilotlarni nomi, INN, viloyat, tuman va holati bo'yicha filtrlaydi."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    inn = django_filters.CharFilter(lookup_expr="icontains")
    region = UUIDInFilter(field_name="region_id", lookup_expr="in")
    district = UUIDInFilter(field_name="district_id", lookup_expr="in")
    status = django_filters.BooleanFilter(field_name="is_active", label="Holat")
    branches_count_min = django_filters.NumberFilter(
        field_name="branches_count", lookup_expr="gte", label="Filiallar soni (dan)"
    )
    branches_count_max = django_filters.NumberFilter(
        field_name="branches_count", lookup_expr="lte", label="Filiallar soni (gacha)"
    )
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = Organization
        fields = [
            "name",
            "inn",
            "region",
            "district",
            "status",
            "branches_count_min",
            "branches_count_max",
            "start_date",
            "end_date",
        ]


class BranchFilter(django_filters.FilterSet):
    """Filiallarni nomi, tashkilot, viloyat, tuman va holati bo'yicha filtrlaydi."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    organization = UUIDInFilter(field_name="organization_id", lookup_expr="in")
    region = UUIDInFilter(field_name="region_id", lookup_expr="in")
    district = UUIDInFilter(field_name="district_id", lookup_expr="in")
    status = django_filters.BooleanFilter(field_name="is_active", label="Holat")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = Branch
        fields = [
            "name",
            "organization",
            "region",
            "district",
            "status",
            "start_date",
            "end_date",
        ]
