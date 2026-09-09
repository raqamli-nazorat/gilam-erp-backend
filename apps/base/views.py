"""
Barcha loyiha ViewSet'lari uchun bazaviy ViewSet klasslari.

Ushbu modul tayyor AutoSchema va DynamicPermission mixinlaridan iborat
standart CRUD va ReadOnly ViewSet klasslarini taqdim etadi.
"""

from rest_framework import viewsets
from apps.base.mixins import (
    DynamicPermissionMixin,
    AutoSchemaMixin,
)


class BaseManageViewSet(AutoSchemaMixin, DynamicPermissionMixin, viewsets.ModelViewSet):
    """
    To'liq CRUD (Create, Read, Update, Delete) operatsiyalari uchun bazaviy ViewSet.
    """

    pass


class BaseReadOnlyViewSet(
    AutoSchemaMixin, DynamicPermissionMixin, viewsets.ReadOnlyModelViewSet
):
    """
    Faqat o'qish (List, Retrieve) operatsiyalari uchun bazaviy ViewSet.
    """

    pass

