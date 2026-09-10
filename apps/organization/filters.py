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
    """Tashkilotlarni nomi, INN, viloyat va tuman bo'yicha filtrlaydi."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    inn = django_filters.CharFilter(lookup_expr="icontains")
    region = UUIDInFilter(field_name="region_id", lookup_expr="in")
    district = UUIDInFilter(field_name="district_id", lookup_expr="in")

    class Meta:
        model = Organization
        fields = ["name", "inn", "region", "district"]


class BranchFilter(django_filters.FilterSet):
    """Filiallarni nomi, tashkilot, viloyat va tuman bo'yicha filtrlaydi."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    organization = UUIDInFilter(field_name="organization_id", lookup_expr="in")
    region = UUIDInFilter(field_name="region_id", lookup_expr="in")
    district = UUIDInFilter(field_name="district_id", lookup_expr="in")

    class Meta:
        model = Branch
        fields = ["name", "organization", "region", "district"]
