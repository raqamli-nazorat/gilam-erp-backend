"""
Hr app ViewSet'lari uchun FilterSet klasslari.
"""

import django_filters

from .models import Position


class PositionFilter(django_filters.FilterSet):
    """Lavozimlarni nomi, holati va yaratilgan sanasi bo'yicha filtrlaydi."""

    name = django_filters.CharFilter(lookup_expr="icontains")
    status = django_filters.BooleanFilter(field_name="is_active", label="Holat")
    start_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="gte", label="Yaratilgan sana (dan)"
    )
    end_date = django_filters.DateFilter(
        field_name="created_at", lookup_expr="lte", label="Yaratilgan sana (gacha)"
    )

    class Meta:
        model = Position
        fields = ["name", "status", "start_date", "end_date"]
