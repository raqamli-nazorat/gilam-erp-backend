from django.db import models

from apps.base.models import BaseModel

from .installment_agreement import InstallmentAgreement


class Payment(BaseModel):
    """To'lov."""

    class PaymentMethod(models.TextChoices):
        CASH = "cash", "Naqd"
        CARD = "card", "Terminal"
        BANK_TRANSFER = "bank_transfer", "Bank o'tkazmasi"
        CLICK = "click", "Click"
        PAYME = "payme", "Payme"
        APELSIN = "apelsin", "Apelsin"

    class PaymentType(models.TextChoices):
        ORDER_PAYMENT = "order_payment", "Sotuv to'lovi"
        DEBT_PAYMENT = "debt_payment", "Nasiya to'lovi"
        DOWN_PAYMENT = "down_payment", "Boshlang'ich muddatli to'lov"

    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.PROTECT,
        related_name="payments",
        db_index=True,
        verbose_name="Tashkilot",
    )
    order = models.ForeignKey(
        "sales.Order",
        on_delete=models.PROTECT,
        related_name="payments",
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Sotuv cheki",
        help_text="Sotuv to'lovi bo'lsa bog'lanadi",
    )
    installment_agreement = models.ForeignKey(
        InstallmentAgreement,
        on_delete=models.PROTECT,
        related_name="payments",
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Muddatli to'lov shartnomasi",
        help_text="Shartnoma bo'yicha to'lov bo'lsa bog'lanadi",
    )
    customer = models.ForeignKey(
        "sales.Customer",
        on_delete=models.PROTECT,
        related_name="payments",
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Mijoz",
        help_text="Nasiya yopilganda kim to'laganini bilish uchun",
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Summa")
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        db_index=True,
        verbose_name="To'lov usuli",
    )
    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType.choices,
        db_index=True,
        verbose_name="To'lov turi",
    )

    class Meta:
        db_table = "finance_payment"
        verbose_name = "To'lov"
        verbose_name_plural = "To'lovlar"

    def __str__(self):
        return f"{self.get_payment_type_display()} — {self.amount}"
