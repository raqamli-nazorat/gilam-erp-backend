from django.db import models

from apps.base.models import BaseModel

from .customer import Customer


class Order(BaseModel):
    """Sotuv cheki (hujjati)."""

    class PaymentStatus(models.TextChoices):
        PAID = "paid", "To'langan"
        PARTIALLY_PAID = "partially_paid", "Qisman to'langan"
        DEBT = "debt", "Nasiya"
        UNPAID = "unpaid", "To'lanmagan"

    class OrderStatus(models.TextChoices):
        PENDING = "pending", "Kutilmoqda"
        COMPLETED = "completed", "Yakunlangan"
        CANCELLED = "cancelled", "Bekor qilingan"

    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.PROTECT,
        related_name="orders",
        db_index=True,
        verbose_name="Tashkilot",
    )
    branch = models.ForeignKey(
        "organization.Branch",
        on_delete=models.PROTECT,
        related_name="orders",
        db_index=True,
        verbose_name="Filial",
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Mijoz",
        help_text="Bo'sh bo'lsa — nomsiz xaridor",
    )
    seller = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="sold_orders",
        db_index=True,
        verbose_name="Sotgan xodim",
    )
    cashier = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="cashier_orders",
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Kassir",
        help_text="Pulni qabul qilgan xodim",
    )
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Chegirmasiz jami summa"
    )
    discount_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name="Chegirma summasi"
    )
    final_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Yakuniy summa"
    )
    paid_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name="To'langan summa"
    )
    debt_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name="Nasiya summa"
    )
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        db_index=True,
        verbose_name="To'lov holati",
    )
    order_status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True,
        verbose_name="Chek holati",
    )
    overlock_included = models.BooleanField(
        default=False, verbose_name="Tikish (ovirlok) xizmati bormi"
    )
    delivery_required = models.BooleanField(
        default=False, verbose_name="Yetkazib berish kerakmi"
    )
    delivery_address = models.TextField(
        blank=True, default="", verbose_name="Yetkazib berish manzili"
    )
    delivery_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Yetkazib berish sanasi"
    )

    class Meta:
        db_table = "sales_order"
        verbose_name = "Sotuv cheki"
        verbose_name_plural = "Sotuv cheklari"

    def __str__(self):
        return f"{self.id} — {self.final_amount}"
