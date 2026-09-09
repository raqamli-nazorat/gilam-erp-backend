"""
Django-filters uchun umumiy va maxsus filter klasslari.

Ushbu modul vergul bilan ajratilgan UUID, son yoki satrlar ro'yxati (in filter)
hamda yaratilgan vaqt (created_at) bo'yicha saralash klasslarini o'z ichiga oladi.
"""

import django_filters


class UUIDInFilter(django_filters.BaseInFilter, django_filters.UUIDFilter):
    """Vergul bilan ajratilgan UUID ro'yxatlarini saralovchi filter."""

    pass


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    """Vergul bilan ajratilgan sonlar ro'yxatlarini saralovchi filter."""

    pass


class CharInFilter(django_filters.BaseInFilter, django_filters.CharFilter):
    """Vergul bilan ajratilgan satrlar ro'yxatlarini saralovchi filter."""

    pass


class BaseFilterSet(django_filters.FilterSet):
    """
    Barcha FilterSet klasslari uchun bazaviy filtr.
    Yaratilgan vaqti (created_at) bo'yicha start_date va end_date berish imkonini beradi.
    """

    start_date = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
    end_date = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
