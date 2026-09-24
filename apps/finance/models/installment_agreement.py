from django.db import models

from apps.base.models import BaseModel


class InstallmentAgreement(BaseModel):
    """Muddatli to'lov (rassrochka) shartnomasi."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Faol"
        CLOSED = "closed", "Tugatilgan"
        OVERDUE = "overdue", "Kechikayotgan"

    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.PROTECT,
        related_name="installment_agreements",
        db_index=True,
        verbose_name="Tashkilot",
    )
    order = models.OneToOneField(
        "sales.Order",
        on_delete=models.PROTECT,
        related_name="installment_agreement",
        verbose_name="Sotuv cheki",
    )
    customer = models.ForeignKey(
        "sales.Customer",
        on_delete=models.PROTECT,
        related_name="installment_agreements",
        db_index=True,
        verbose_name="Mijoz",
    )
    agreement_number = models.CharField(
        max_length=100, unique=True, verbose_name="Shartnoma raqami"
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Jami summa (ustamalari bilan)",
    )
    down_payment = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Boshlang'ich to'lov"
    )
    remaining_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name="Qolgan muddatli to'lanadigan summa",
    )
    number_of_months = models.PositiveIntegerField(verbose_name="Necha oyga bo'lingan")
    markup_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="Ustama foizi (rassrochka ustamasi)",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
        verbose_name="Holati",
    )

    class Meta:
        db_table = "finance_installment_agreement"
        verbose_name = "Muddatli to'lov shartnomasi"
        verbose_name_plural = "Muddatli to'lov shartnomalari"

    def __str__(self):
        return self.agreement_number
