from decimal import Decimal

from django.db import transaction
from django.db.models import Sum
from rest_framework.exceptions import ValidationError

from apps.warehouse.models import CarpetRoll, ProductStock, StockTransaction

from ..models import SupplierPurchase, SupplierPurchaseItem
from .supplier_purchase_item import compute_subtotal, resolve_product_party


def create_supplier_purchase_with_items(
    *,
    organization,
    supplier,
    warehouse,
    items,
    created_by=None,
    paid_amount=None,
):
    """Xarid hujjatini va uning barcha qatorlarini bitta tranzaksiyada yaratadi.

    Har bir qator uchun mavjud `product_party` tanlanishi yoki `product_party_data`
    orqali yangisi yaratilishi mumkin. `subtotal` va hujjatning `total_amount`/
    `debt_amount`i klientdan qabul qilinmaydi — shu yerda hisoblanadi.
    """
    paid_amount = paid_amount or Decimal(0)

    with transaction.atomic():
        purchase = SupplierPurchase.objects.create(
            organization=organization,
            supplier=supplier,
            warehouse=warehouse,
            created_by=created_by,
            total_amount=Decimal(0),
            paid_amount=paid_amount,
            debt_amount=Decimal(0),
        )

        total_amount = Decimal(0)
        purchase_items = []

        for item_data in items:
            product_party = resolve_product_party(
                warehouse=warehouse,
                product_party=item_data.get("product_party"),
                product_party_data=item_data.get("product_party_data"),
            )

            width = item_data["width"]
            length = item_data.get("length")
            total_length_meters = item_data.get("total_length_meters")
            quantity = item_data.get("quantity") or 1
            price_per_sqm = item_data["price_per_sqm"]

            subtotal = compute_subtotal(
                width=width,
                length=length,
                total_length_meters=total_length_meters,
                quantity=quantity,
                price_per_sqm=price_per_sqm,
            )
            total_amount += subtotal

            purchase_items.append(
                SupplierPurchaseItem(
                    purchase=purchase,
                    product_party=product_party,
                    roll_number=item_data.get("roll_number", ""),
                    width=width,
                    length=length,
                    quantity=quantity,
                    total_length_meters=total_length_meters,
                    price_per_sqm=price_per_sqm,
                    subtotal=subtotal,
                )
            )

        SupplierPurchaseItem.objects.bulk_create(purchase_items)

        purchase.total_amount = total_amount
        purchase.debt_amount = total_amount - paid_amount
        purchase.save(update_fields=["total_amount", "debt_amount"])

    return purchase


def recalculate_totals(purchase):
    """Hujjatning `total_amount`/`debt_amount`ini faol qatorlar yig'indisidan qayta hisoblaydi."""
    total_amount = purchase.items.active().aggregate(total=Sum("subtotal"))[
        "total"
    ] or Decimal(0)
    purchase.total_amount = total_amount
    purchase.debt_amount = total_amount - purchase.paid_amount
    purchase.save(update_fields=["total_amount", "debt_amount"])
    return purchase


def confirm_supplier_purchase(purchase):
    """Hujjatni tasdiqlaydi: ombor qoldig'ini oshiradi, `StockTransaction`/`CarpetRoll` yaratadi."""
    if purchase.status == SupplierPurchase.Status.CONFIRMED:
        raise ValidationError("Hujjat allaqachon tasdiqlangan.")

    items = list(purchase.items.active().select_related("product_party"))
    if not items:
        raise ValidationError("Tasdiqlash uchun kamida bitta qator bo'lishi kerak.")

    with transaction.atomic():
        for item in items:
            length = item.length or item.total_length_meters or Decimal(0)

            StockTransaction.objects.create(
                organization=purchase.organization,
                product_party=item.product_party,
                to_warehouse=purchase.warehouse,
                transaction_type=StockTransaction.TransactionType.IN,
                ref_type=StockTransaction.RefType.PURCHASE,
                ref_id=purchase.id,
                quantity=item.quantity,
                length_meters=length,
            )

            stock, _ = ProductStock.objects.get_or_create(
                warehouse=purchase.warehouse,
                product_party=item.product_party,
                defaults={"quantity": 0, "total_length_meters": Decimal(0)},
            )
            stock.quantity += item.quantity
            stock.total_length_meters += length
            stock.save(update_fields=["quantity", "total_length_meters"])

            if item.roll_number:
                CarpetRoll.objects.create(
                    product_party=item.product_party,
                    warehouse=purchase.warehouse,
                    roll_number=item.roll_number,
                    initial_length_meters=length,
                    current_length_meters=length,
                )

        purchase.status = SupplierPurchase.Status.CONFIRMED
        purchase.save(update_fields=["status"])

    return purchase


def revert_supplier_purchase(purchase):
    """Hujjatni qoralamaga qaytaradi: ombor qoldig'ini kamaytiradi, tegishli
    `CarpetRoll`larni bekor qiladi va muvozanatlovchi `StockTransaction` yozadi.

    Agar shu kirim orqali kelgan tovar allaqachon sotilgan/harakatlangan bo'lsa
    (qoldiq yetarli emas yoki rulon tegilgan), qaytarish rad etiladi.
    """
    if purchase.status == SupplierPurchase.Status.DRAFT:
        raise ValidationError("Hujjat hali tasdiqlanmagan.")

    items = list(purchase.items.active().select_related("product_party"))

    with transaction.atomic():
        for item in items:
            length = item.length or item.total_length_meters or Decimal(0)

            stock = ProductStock.objects.filter(
                warehouse=purchase.warehouse, product_party=item.product_party
            ).first()
            if (
                not stock
                or stock.quantity < item.quantity
                or stock.total_length_meters < length
            ):
                raise ValidationError(
                    "Ombordagi qoldiq yetarli emas, ushbu hujjatni qaytarib bo'lmaydi."
                )

            roll = None
            if item.roll_number:
                roll = (
                    CarpetRoll.objects.active()
                    .filter(
                        warehouse=purchase.warehouse,
                        product_party=item.product_party,
                        roll_number=item.roll_number,
                    )
                    .first()
                )
                if roll and roll.current_length_meters != roll.initial_length_meters:
                    raise ValidationError(
                        "Ushbu kirim orqali kelgan tovar allaqachon"
                        " sotilgan/harakatlangan, qaytarib bo'lmaydi."
                    )

            stock.quantity -= item.quantity
            stock.total_length_meters -= length
            stock.save(update_fields=["quantity", "total_length_meters"])

            if roll:
                roll.delete()

            StockTransaction.objects.create(
                organization=purchase.organization,
                product_party=item.product_party,
                from_warehouse=purchase.warehouse,
                transaction_type=StockTransaction.TransactionType.OUT,
                ref_type=StockTransaction.RefType.ADJUSTMENT,
                ref_id=purchase.id,
                quantity=item.quantity,
                length_meters=length,
            )

        purchase.status = SupplierPurchase.Status.DRAFT
        purchase.save(update_fields=["status"])

    return purchase
