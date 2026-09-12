from django.contrib.auth.models import update_last_login
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken

from ..models import User


def get_user_auth_payload(user: User) -> dict:
    if user.is_system_admin:
        permissions_list = ["*"]
    else:
        permissions_list = sorted(list(user.get_role_permissions()))

    return {
        "id": str(user.id),
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "is_system_admin": user.is_system_admin,
        "all_branches": user.all_branches,
        "role": (
            {"id": str(user.role.id), "name": user.role.name}
            if user.role
            else None
        ),
        "organization": (
            {
                "id": str(user.organization.id),
                "name": user.organization.name,
                "inn": getattr(user.organization, "inn", None),
            }
            if user.organization
            else None
        ),
        "branch": (
            {"id": str(user.branch.id), "name": user.branch.name}
            if user.branch
            else None
        ),
        "employee": (
            {
                "id": str(user.employee.id),
                "full_name": user.employee.full_name,
            }
            if user.employee
            else None
        ),
        "permissions": permissions_list,
        "accessible_branches": [
            {"id": str(b.id), "name": b.name}
            for b in user.get_accessible_branches()
        ],
    }


class LoginSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["id"] = str(user.id)
        token["full_name"] = user.full_name
        token["is_system_admin"] = user.is_system_admin
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        update_last_login(None, user)
        data["user"] = get_user_auth_payload(user)
        return data


class RefreshTokenSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = RefreshToken(attrs["refresh"])
        user_id = refresh.get("user_id")

        try:
            user = (
                User.objects.active()
                .select_related("role", "organization", "branch", "employee")
                .get(id=user_id)
            )
            data["user"] = get_user_auth_payload(user)
        except User.DoesNotExist:
            pass

        return data
