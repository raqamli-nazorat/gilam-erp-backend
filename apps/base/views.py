from rest_framework import viewsets

from apps.base.mixins import (
    AutoSchemaMixin,
    DynamicPermissionMixin,
    TenantBranchScopeMixin,
)


class BaseManageViewSet(
    AutoSchemaMixin,
    DynamicPermissionMixin,
    TenantBranchScopeMixin,
    viewsets.ModelViewSet,
):
    pass


class BaseReadOnlyViewSet(
    AutoSchemaMixin,
    DynamicPermissionMixin,
    TenantBranchScopeMixin,
    viewsets.ReadOnlyModelViewSet,
):
    pass
