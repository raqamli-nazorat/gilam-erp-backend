from django.contrib.auth.models import Permission
from django.db.models import Q
from rest_framework.response import Response

from apps.base.views import BaseReadOnlyViewSet

from ..serializers.permission import PermissionSerializer
from ..serializers.role import SYSTEM_APP_LABELS


class PermissionViewSet(BaseReadOnlyViewSet):


    serializer_class = PermissionSerializer
    pagination_class = None

    def get_queryset(self):
        user = self.request.user

        qs = (
            Permission.objects.select_related("content_type")
            .exclude(content_type__app_label__in=SYSTEM_APP_LABELS)
            .order_by("content_type__model", "codename")
        )

        if not user.is_system_admin:
            from ..serializers.role import SYSTEM_PERMISSIONS

            system_q = Q()
            for sys_perm in SYSTEM_PERMISSIONS:
                app, code = sys_perm.split(".")
                system_q |= Q(content_type__app_label=app, codename=code)
            qs = qs.exclude(system_q)

        return qs


    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)

        grouped_data = {}
        for perm in serializer.data:
            group_key = perm["model_name"]
            if group_key not in grouped_data:
                grouped_data[group_key] = []
            grouped_data[group_key].append(
                {"id": perm["id"], "name": perm["name"], "codename": perm["codename"]}
            )

        return Response(grouped_data)
