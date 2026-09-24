from django.db import models

from apps.base.models import BaseModel


class DebtLedger(BaseModel):
    """Nasiya daftari — qarzlarni monitoring qilish uchun umumiy jadval."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Faol"
        PAID = "paid", "To'langan"
        OVERDUE = "overdue", "Muddati o'tgan"

    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.PROTECT,
        related_name="debt_ledgers",
        db_index=True,
        verbose_name="Tashkilot",
    )
    customer = models.ForeignKey(
        "sales.Customer",
        on_delete=models.PROTECT,
        related_name="debt_ledgers",
        db_index=True,
        verbose_name="Mijoz",
    )
    order = models.ForeignKey(
        "sales.Order",
        on_delete=models.PROTECT,
        related_name="debt_ledgers",
        db_index=True,
        verbose_name="Sotuv cheki",
    )
    total_debt = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Jami qarz summasi"
    )
    remaining_debt = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Qolgan qarz summasi"
    )
    due_date = models.DateTimeField(
        null=True, blank=True, verbose_name="To'lash oxirgi muddati"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        verbose_name="Holati",
    )

    class Meta:
        db_table = "finance_debt_ledger"
        verbose_name = "Nasiya daftari"
        verbose_name_plural = "Nasiya daftarlari"

    def __str__(self):
        return f"{self.customer} — {self.remaining_debt}"
