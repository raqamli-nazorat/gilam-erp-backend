from django.apps import apps
from django.db.models import OuterRef, Q, Subquery
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.models import User, UserBlockLog
from apps.base.models import BaseModel
from apps.hr.models import RecruitmentDismissal
from apps.organization.models import Branch, Organization


def _scoped_queryset(model, user):
    queryset = model._default_manager.all()
    if user.is_system_admin:
        return queryset

    fields = {field.name for field in model._meta.get_fields()}
    if model is Organization:
        return queryset.filter(id=user.organization_id)
    if model is Branch:
        return user.get_accessible_branches(include_inactive=True)
    if model is User:
        return queryset.filter(employee__organization_id=user.organization_id)
    if "branch" in fields and "organization" in fields:
        branch_ids = user.get_accessible_branches(include_inactive=True).values_list(
            "id", flat=True
        )
        return queryset.filter(
            organization_id=user.organization_id, branch_id__in=branch_ids
        )
    if "branch" in fields:
        accessible_branch_ids = user.get_accessible_branches(
            include_inactive=True
        ).values_list("id", flat=True)
        return queryset.filter(branch_id__in=accessible_branch_ids)
    if "organization" in fields:
        return queryset.filter(organization_id=user.organization_id)
    return queryset


class CountsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        result = {
            "organizations": {},
            "branches": {},
            "users": {},
            "recruitments": 0,
            "dismissals": 0,
            "models": {},
        }

        for model in apps.get_models():
            app_config = apps.get_app_config(model._meta.app_label)
            if (
                not app_config.name.startswith("apps.")
                or model._meta.abstract
                or not issubclass(model, BaseModel)
            ):
                continue

            permission = f"{model._meta.app_label}.view_{model._meta.model_name}"
            if not request.user.has_perm(permission):
                continue

            queryset = _scoped_queryset(model, request.user)
            total = queryset.count()
            key = f"{model._meta.app_label}.{model._meta.model_name}"
            result["models"][key] = total

            if model is Organization:
                active = queryset.filter(is_active=True, is_suspended=False).count()
                suspended = queryset.filter(is_active=True, is_suspended=True).count()
                result["organizations"] = {
                    "all": total,
                    "active": active,
                    "suspended": suspended,
                }
            elif model is Branch:
                active = queryset.filter(is_active=True, is_closed=False).count()
                closed = queryset.filter(is_active=True, is_closed=True).count()
                result["branches"] = {
                    "all": total,
                    "active": active,
                    "closed": closed,
                }
            elif model is User:
                latest_block = UserBlockLog.objects.filter(user=OuterRef("pk")).order_by(
                    "-created_at", "-pk"
                )
                queryset = queryset.annotate(
                    latest_block_type=Subquery(latest_block.values("type")[:1])
                )
                blocked = queryset.filter(
                    is_active=True, latest_block_type=UserBlockLog.Type.BLOCK
                ).count()
                active = queryset.filter(is_active=True).filter(
                    Q(latest_block_type__isnull=True)
                    | ~Q(latest_block_type=UserBlockLog.Type.BLOCK)
                ).count()
                result["users"] = {
                    "all": total,
                    "active": active,
                    "blocked": blocked,
                }
            elif model is RecruitmentDismissal:
                result["recruitments"] = queryset.filter(
                    type=RecruitmentDismissal.Type.RECRUITMENT
                ).count()
                result["dismissals"] = queryset.filter(
                    type=RecruitmentDismissal.Type.DISMISSAL
                ).count()

        return Response(result)
