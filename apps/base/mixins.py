from drf_spectacular.utils import extend_schema

from apps.base.permissions import FullDjangoModelPermissions


class DynamicPermissionMixin:

    permission_classes = [FullDjangoModelPermissions]


class TenantBranchScopeMixin:

    def get_queryset(self):
        qs = super().get_queryset()
        request = getattr(self, "request", None)
        user = getattr(request, "user", None) if request else None

        if not user or not user.is_authenticated:
            return qs.none()


        if getattr(user, "is_system_admin", False):
            return qs

        model = qs.model
        fields = {f.name for f in model._meta.get_fields()}


        if (
            model._meta.app_label == "organization"
            and model._meta.model_name == "organization"
        ):
            return qs.filter(id=user.organization_id)


        if (
            model._meta.app_label == "organization"
            and model._meta.model_name == "branch"
        ):
            return user.get_accessible_branches()


        if "branch" in fields and "organization" in fields:
            branch_ids = set()
            if user.role and user.role.branches.exists():
                branch_ids.update(user.role.branches.values_list("id", flat=True))
            if user.branch_id:
                branch_ids.add(user.branch_id)
            if branch_ids:
                return qs.filter(
                    organization_id=user.organization_id, branch_id__in=branch_ids
                )
            return qs.filter(organization_id=user.organization_id)

        if "branch" in fields:
            accessible_branch_ids = user.get_accessible_branches().values_list(
                "id", flat=True
            )
            return qs.filter(branch_id__in=accessible_branch_ids)


        if "organization" in fields:
            return qs.filter(organization_id=user.organization_id)

        return qs

    def perform_create(self, serializer):
        request = getattr(self, "request", None)
        user = getattr(request, "user", None) if request else None
        extra_kwargs = {}

        if user and not getattr(user, "is_system_admin", False):
            model = serializer.Meta.model
            fields = {f.name for f in model._meta.get_fields()}


            if "organization" in fields:
                extra_kwargs["organization"] = user.organization



            if "branch" in fields:
                branch = serializer.validated_data.get("branch")
                accessible_branch_ids = set(
                    user.get_accessible_branches().values_list("id", flat=True)
                )
                if branch and branch.id not in accessible_branch_ids:
                    from rest_framework.exceptions import ValidationError

                    raise ValidationError(
                        {
                            "branch": "Sizda ushbu filial uchun ma'lumot yaratish huquqi yo'q."
                        }
                    )

        serializer.save(**extra_kwargs)


class AutoSchemaMixin:

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        tag_name = None

        is_viewset = False
        if (
            cls.__name__.endswith("ViewSet")
            or hasattr(cls, "get_view_name")
            and "ViewSet" in cls.__name__
        ):
            is_viewset = True

        if is_viewset:
            queryset = getattr(cls, "queryset", None)
            if queryset is not None:
                tag_name = queryset.model.__name__
            elif hasattr(cls, "get_queryset") and callable(cls.get_queryset):
                try:
                    dummy_instance = cls()
                    qs = dummy_instance.get_queryset()
                    if hasattr(qs, "model"):
                        tag_name = qs.model.__name__
                except Exception:
                    pass

            if (
                not tag_name
                and hasattr(cls, "serializer_class")
                and cls.serializer_class
            ):
                meta = getattr(cls.serializer_class, "Meta", None)
                if meta and hasattr(meta, "model"):
                    tag_name = meta.model.__name__
            if not tag_name:
                tag_name = cls.__name__.replace("ViewSet", "")
        else:
            module_parts = cls.__module__.split(".")
            if len(module_parts) >= 3 and module_parts[0] == "apps":
                main_app = module_parts[1].capitalize()
                sub_app = module_parts[2].capitalize()
                tag_name = f"{main_app} ({sub_app})"
            else:
                tag_name = cls.__name__
                for suffix in ["APIView", "View"]:
                    if tag_name.endswith(suffix):
                        tag_name = tag_name[: -len(suffix)]
                        break

        if tag_name:
            extend_schema(tags=[tag_name])(cls)
