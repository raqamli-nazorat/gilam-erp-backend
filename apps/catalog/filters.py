"""
Catalog app ViewSet'lari uchun FilterSet klasslari.
"""

import django_filters

from .models import ProductColor, Quality, Unit


class QualityFilter(django_filters.FilterSet):
    """Sifatlarni nomi, holati va yaratilgan sanasi bo'yicha filtrlaydi."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    status = django_filters.BooleanFilter(field_name="is_active", label="Holat")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = Quality
        fields = ["name", "status", "start_date", "end_date"]


class UnitFilter(django_filters.FilterSet):
    """O'lchov birliklarini nomi, holati va yaratilgan sanasi bo'yicha filtrlaydi."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    status = django_filters.BooleanFilter(field_name="is_active", label="Holat")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = Unit
        fields = ["name", "status", "start_date", "end_date"]


class ProductColorFilter(django_filters.FilterSet):
    """Ranglarni nomi, holati va yaratilgan sanasi bo'yicha filtrlaydi."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    status = django_filters.BooleanFilter(field_name="is_active", label="Holat")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = ProductColor
        fields = ["name", "status", "start_date", "end_date"]
