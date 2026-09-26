from django.db.models import OuterRef, Subquery
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from apps.base.views import BaseManageViewSet

from ..filters import UserFilter
from ..models import User, UserBlockLog
from ..serializers import UserSerializer


class UserViewSet(BaseManageViewSet):
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = UserFilter
    search_fields = ["full_name", "phone_number"]
    ordering_fields = ["full_name", "created_at"]
    action_permissions = {
        "block": ["accounts.block_user"],
        "unblock": ["accounts.unblock_user"],
    }

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return User.objects.none()

        latest_block = UserBlockLog.objects.filter(user=OuterRef("pk")).order_by(
            "-created_at"
        )
        qs = (
            User.objects.active()
            .select_related("role", "employee__organization", "employee__branch")
            .annotate(
                latest_block_type=Subquery(latest_block.values("type")[:1]),
                latest_block_reason=Subquery(latest_block.values("reason")[:1]),
                latest_block_at=Subquery(latest_block.values("created_at")[:1]),
                latest_block_actor_name=Subquery(
                    latest_block.values("actor__full_name")[:1]
                ),
            )
        )
        if user.is_system_admin:
            return qs
        return qs.filter(employee__organization=user.organization)

    @action(detail=False, methods=["get"])
    def count(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        total = queryset.count()
        blocked = queryset.filter(latest_block_type=UserBlockLog.Type.BLOCK).count()
        return Response({"all": total, "active": total - blocked, "blocked": blocked})

    @action(detail=True, methods=["patch"])
    def block(self, request, pk=None):
        """Foydalanuvchini bloklaydi (login taqiqlanadi, ro'yxatda ko'rinishda qoladi)."""
        reason = request.data.get("reason")
        if not reason or not str(reason).strip():
            return Response(
                {"reason": ["Bloklash sababini kiritish majburiy."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        target_user = self.get_object()
        UserBlockLog.objects.create(
            user=target_user,
            type=UserBlockLog.Type.BLOCK,
            reason=str(reason).strip(),
            actor=request.user,
        )
        return Response(
            {
                "id": str(target_user.id),
                "full_name": target_user.full_name,
                "is_blocked": True,
                "detail": "Foydalanuvchi bloklandi.",
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=True, methods=["patch"])
    def unblock(self, request, pk=None):
        """Foydalanuvchini blokdan chiqaradi."""
        target_user = self.get_object()
        UserBlockLog.objects.create(
            user=target_user,
            type=UserBlockLog.Type.UNBLOCK,
            actor=request.user,
        )
        return Response(
            {
                "id": str(target_user.id),
                "full_name": target_user.full_name,
                "is_blocked": False,
                "detail": "Foydalanuvchi blokdan chiqarildi.",
            },
            status=status.HTTP_200_OK,
        )
