from rest_framework import permissions


class FullDjangoModelPermissions(permissions.DjangoModelPermissions):

    perms_map = {
        "GET": ["%(app_label)s.view_%(model_name)s"],
        "OPTIONS": [],
        "HEAD": [],
        "POST": ["%(app_label)s.add_%(model_name)s"],
        "PUT": ["%(app_label)s.change_%(model_name)s"],
        "PATCH": ["%(app_label)s.change_%(model_name)s"],
        "DELETE": ["%(app_label)s.delete_%(model_name)s"],
    }

    def get_custom_action_permissions(self, view, model):
        action_name = getattr(view, "action", None)
        if not action_name:
            return None


        action_permissions = getattr(view, "action_permissions", None)
        if isinstance(action_permissions, dict) and action_name in action_permissions:
            perms = action_permissions[action_name]
            if isinstance(perms, str):
                return [perms]
            return list(perms)


        action_handler = getattr(view, action_name, None)
        if action_handler and hasattr(action_handler, "permission_required"):
            perm = action_handler.permission_required
            if isinstance(perm, (list, tuple, set)):
                return list(perm)
            return [perm]


        app_label = model._meta.app_label
        model_name = model._meta.model_name

        candidates = {
            action_name,
            f"{action_name}_{model_name}",
            f"can_{action_name}",
            f"can_{action_name}_{model_name}",
        }

        model_perms = getattr(model._meta, "permissions", ())
        for perm_tuple in model_perms:
            codename = perm_tuple[0]
            if codename in candidates:
                return [f"{app_label}.{codename}"]

        return None

    def has_permission(self, request, view):
        if getattr(view, "_ignore_model_permissions", False):
            return True

        if not request.user or (
            not request.user.is_authenticated and self.authenticated_users_only
        ):
            return False


        if getattr(request.user, "is_system_admin", False):
            return True

        queryset = self._queryset(view)
        model = queryset.model


        action_name = getattr(view, "action", None)
        standard_actions = {
            "list",
            "retrieve",
            "create",
            "update",
            "partial_update",
            "destroy",
        }

        if action_name and action_name not in standard_actions:
            custom_perms = self.get_custom_action_permissions(view, model)
            if custom_perms is not None:
                return request.user.has_perms(custom_perms)

        perms = self.get_required_permissions(request.method, model)
        return request.user.has_perms(perms)

    def has_object_permission(self, request, view, obj):
        user = request.user
        if getattr(user, "is_system_admin", False):
            return True


        if hasattr(obj, "branch_id") and obj.branch_id:
            accessible_ids = set(
                user.get_accessible_branches().values_list("id", flat=True)
            )
            if obj.branch_id not in accessible_ids:
                return False


        if hasattr(obj, "organization_id") and obj.organization_id:
            if obj.organization_id != user.organization_id:
                return False

        return True


class IsOwnerOrStaff(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff or getattr(
            request.user, "is_system_admin", False
        ):
            return True

        if hasattr(obj, "user"):
            return obj.user == request.user

        return obj == request.user
