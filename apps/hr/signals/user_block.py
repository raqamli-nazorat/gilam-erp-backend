from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.accounts.models import UserBlockLog
from apps.accounts.services import is_user_blocked

from ..models import RecruitmentDismissal
from ..services import get_active_recruitment_records


@receiver(post_save, sender=RecruitmentDismissal)
def sync_user_block_on_recruitment_dismissal(sender, instance, created, **kwargs):
    """Xodim hech qaysi filialda ishlamay qolsa bloklaydi, birortasida ishlay boshlasa blokdan chiqaradi.

    Xodim bir nechta filialda ishlashi mumkin — shuning uchun bitta filialdan
    bo'shatish, boshqa filialda hali ishlayotgan bo'lsa, akkauntni bloklamaydi.
    """
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
    is_employed_anywhere = bool(get_active_recruitment_records(instance.employee))

    if is_employed_anywhere and is_user_blocked(user):
        UserBlockLog.objects.create(
            user=user,
            type=UserBlockLog.Type.UNBLOCK,
            actor=actor,
        )
    elif not is_employed_anywhere and not is_user_blocked(user):
        UserBlockLog.objects.create(
            user=user,
            type=UserBlockLog.Type.BLOCK,
            reason=instance.dismissal_reason
            if instance.type == RecruitmentDismissal.Type.DISMISSAL
            else "",
            actor=actor,
        )
