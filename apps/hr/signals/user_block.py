from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import UserBlockLog
from apps.accounts.services import is_user_blocked

from ..models import RecruitmentDismissal


@receiver(post_save, sender=RecruitmentDismissal)
def sync_user_block_on_recruitment_dismissal(sender, instance, created, **kwargs):
    """Tasdiqlangan ishdan chiqarishda bloklaydi, ishga olishda blokdan chiqaradi."""
    if (
        not instance.is_active
        or instance.status != RecruitmentDismissal.Status.APPROVED
        or getattr(instance, "_old_status", None)
        == RecruitmentDismissal.Status.APPROVED
    ):
        return

    user = getattr(instance.employee, "user_account", None)
    if not user:
        return

    actor = getattr(instance, "_actor", None)

    if instance.type == RecruitmentDismissal.Type.DISMISSAL:
        UserBlockLog.objects.create(
            user=user,
            type=UserBlockLog.Type.BLOCK,
            reason=instance.dismissal_reason,
            actor=actor,
        )
    elif instance.type == RecruitmentDismissal.Type.RECRUITMENT and is_user_blocked(
        user
    ):
        UserBlockLog.objects.create(
            user=user,
            type=UserBlockLog.Type.UNBLOCK,
            actor=actor,
        )
