from django.db.models import Count, IntegerField, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import RoleFilter
from ..models import Role, User
from ..serializers import RoleSerializer


class RoleViewSet(BaseManageViewSet):


    serializer_class = RoleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = RoleFilter
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Role.objects.none()

        qs = Role.objects.active()
        if not user.is_system_admin:
            qs = qs.filter(organization=user.organization)

        perms_subq = (
            Role.permissions.through.objects.filter(role_id=OuterRef("pk"))
            .values("role_id")
            .annotate(c=Count("permission_id"))
            .values("c")
        )

        users_subq = (
            User.objects.filter(role_id=OuterRef("pk"), is_active=True)
            .values("role_id")
            .annotate(c=Count("id"))
            .values("c")
        )

        qs = qs.annotate(
            permissions_count=Coalesce(
                Subquery(perms_subq, output_field=IntegerField()), 0
            ),
            users_count=Coalesce(
                Subquery(users_subq, output_field=IntegerField()), 0
            ),
        ).select_related("organization")

        if self.action != "list":
            qs = qs.prefetch_related("permissions")

        return qs

    @property
    def serializer_fields(self):
        if self.action == "list":
            return [
                "id",
                "name",
                "organization",
                "is_system",
                "permissions_count",
                "users_count",
                "created_at",
                "updated_at",
            ]
        return None

    def perform_destroy(self, instance):
        if instance.is_system:
            raise ValidationError("Tizim asosiy rolini o'chirib bo'lmaydi.")
        super().perform_destroy(instance)
