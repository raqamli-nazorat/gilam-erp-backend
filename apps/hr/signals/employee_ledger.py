from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from ..models import EmployeeLedger, RecruitmentDismissal


@receiver(pre_save, sender=RecruitmentDismissal)
def track_recruitment_dismissal_changes(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = RecruitmentDismissal.objects.get(pk=instance.pk)
            instance._old_position_id = old.position_id
            instance._old_status = old.status
        except RecruitmentDismissal.DoesNotExist:
            instance._old_position_id = None
            instance._old_status = None
    else:
        instance._old_position_id = None
        instance._old_status = None


@receiver(post_save, sender=RecruitmentDismissal)
def create_employee_ledger_entry(sender, instance, created, **kwargs):
    if not instance.is_active:
        return

    old_status = getattr(instance, "_old_status", None)
    just_approved = (
        instance.status == RecruitmentDismissal.Status.APPROVED
        and old_status != RecruitmentDismissal.Status.APPROVED
    )
    if just_approved and instance.type == RecruitmentDismissal.Type.DISMISSAL:
        EmployeeLedger.objects.create(
            branch=instance.branch,
            employee=instance.employee,
            type=EmployeeLedger.Type.DISMISSAL_WORK,
        )
    elif just_approved and instance.type == RecruitmentDismissal.Type.RECRUITMENT:
        previous_rec = (
            RecruitmentDismissal.objects.filter(
                employee=instance.employee,
                is_active=True,
                status=RecruitmentDismissal.Status.APPROVED,
            )
            .exclude(id=instance.id)
            .order_by("-rec_dism_date", "-created_at")
            .first()
        )
        if (
            previous_rec
            and previous_rec.type == RecruitmentDismissal.Type.RECRUITMENT
            and previous_rec.position_id != instance.position_id
        ):
            EmployeeLedger.objects.create(
                branch=instance.branch,
                employee=instance.employee,
                type=EmployeeLedger.Type.CHANGE_POSITION,
            )
        else:
            EmployeeLedger.objects.create(
                branch=instance.branch,
                employee=instance.employee,
                type=EmployeeLedger.Type.RECRUITMENT,
            )
    elif (
        instance.status == RecruitmentDismissal.Status.APPROVED
        and old_status == RecruitmentDismissal.Status.APPROVED
    ):
        old_position_id = getattr(instance, "_old_position_id", None)
        if (
            old_position_id
            and instance.position_id
            and old_position_id != instance.position_id
        ):
            EmployeeLedger.objects.create(
                branch=instance.branch,
                employee=instance.employee,
                type=EmployeeLedger.Type.CHANGE_POSITION,
            )
