from django.db import models, transaction

from apps.base.models import BaseModel

from .supplier import Supplier

DOCUMENT_NUMBER_PREFIX = "KR-"


class SupplierPurchase(BaseModel):
    """Ta'minotchidan omborga mahsulot kirimi (xarid hujjati)."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Qoralama"
        CONFIRMED = "confirmed", "Tasdiqlangan"

    organization = models.ForeignKey(
        "organization.Organization",
        on_delete=models.PROTECT,
        related_name="supplier_purchases",
        db_index=True,
        verbose_name="Tashkilot",
    )
    document_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        verbose_name="Hujjat raqami",
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name="purchases",
        db_index=True,
        verbose_name="Yetkazuvchi",
    )
    warehouse = models.ForeignKey(
        "warehouse.Warehouse",
        on_delete=models.PROTECT,
        related_name="supplier_purchases",
        db_index=True,
        verbose_name="Ombor",
    )
    created_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.PROTECT,
        related_name="supplier_purchases_created",
        null=True,
        blank=True,
        db_index=True,
        verbose_name="Muallif",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        verbose_name="Holat",
    )
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Jami summa"
    )
    paid_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name="To'langan summa"
    )
    debt_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0, verbose_name="Qarz summa"
    )

    class Meta:
        db_table = "procurement_supplier_purchase"
        verbose_name = "Xarid hujjati"
        verbose_name_plural = "Xarid hujjatlari"

    def save(self, *args, **kwargs):
        """Hujjat raqami bo'sh bo'lsa, tashkilot bo'yicha ketma-ket generatsiya qilinadi."""
        if not self.document_number:
            self.document_number = self._generate_document_number()
        super().save(*args, **kwargs)

    def _generate_document_number(self):
        """Tashkilot doirasida 'KR-0001' formatidagi navbatdagi raqamni topadi."""
        with transaction.atomic():
            last = (
                SupplierPurchase.objects.select_for_update()
                .filter(organization=self.organization)
                .exclude(document_number="")
                .order_by("-created_at")
                .first()
            )
            last_seq = 0
            if last and last.document_number.startswith(DOCUMENT_NUMBER_PREFIX):
                try:
                    last_seq = int(last.document_number[len(DOCUMENT_NUMBER_PREFIX) :])
                except ValueError:
                    last_seq = 0
            return f"{DOCUMENT_NUMBER_PREFIX}{last_seq + 1:04d}"

    def __str__(self):
        return f"{self.document_number} — {self.supplier}"
