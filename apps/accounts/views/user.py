from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from apps.base.views import BaseManageViewSet

from ..filters import UserFilter
from ..models import User
from ..serializers import UserSerializer


class UserViewSet(BaseManageViewSet):


    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    search_fields = ["full_name", "phone_number"]
    ordering_fields = ["full_name", "created_at"]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()
        qs = User.objects.active().select_related(
            "role", "organization", "branch", "employee"
        )
        if user.is_system_admin:
            return qs
        return qs.filter(organization=user.organization)
