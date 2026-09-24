from django.db import models

from apps.base.models import BaseModel

from .installment_agreement import InstallmentAgreement


class InstallmentSchedule(BaseModel):
    """Muddatli to'lov shartnomasi bo'yicha oylik to'lov grafigi."""

    class Status(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        PAID = "paid", "To'langan"
        PARTIALLY_PAID = "partially_paid", "Qisman to'langan"
        OVERDUE = "overdue", "Kechikkan"

    agreement = models.ForeignKey(
        InstallmentAgreement,
        on_delete=models.CASCADE,
        related_name="schedules",
        db_index=True,
        verbose_name="Shartnoma",
    )
    payment_number = models.PositiveIntegerField(verbose_name="Nechinchi oylik to'lov")
    due_date = models.DateField(verbose_name="To'lov muddati")
    amount_to_pay = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="To'lanishi kerak bo'lgan oylik qism",
    )
    paid_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        verbose_name="Haqiqatda to'langan qism",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
        verbose_name="Holati",
    )

    class Meta:
        db_table = "finance_installment_schedule"
        verbose_name = "Oylik to'lov grafigi"
        verbose_name_plural = "Oylik to'lov grafiklari"

    def __str__(self):
        return f"{self.agreement} — {self.payment_number}"
