from decimal import Decimal

from django.db import transaction

from apps.catalog.models import ProductParty

from ..models import SupplierPurchaseItem


def resolve_product_party(*, warehouse, product_party=None, product_party_data=None):
    """Qator uchun mahsulot partiyasini aniqlaydi — mavjudini qaytaradi yoki yangisini yaratadi."""
    if product_party_data:
        return ProductParty.objects.create(
            branch=warehouse.branch, **product_party_data
        )
    return product_party


def compute_subtotal(
    *, width, length=None, total_length_meters=None, quantity=1, price_per_sqm
):
    """Qator summasini hisoblaydi: eni x (bo'yi yoki rulon uzunligi) x soni x narx."""
    effective_length = length or total_length_meters or Decimal(0)
    effective_quantity = quantity if quantity is not None else 1
    return width * effective_length * effective_quantity * price_per_sqm


def create_purchase_item(
    *,
    purchase,
    product_party=None,
    product_party_data=None,
    roll_number="",
    width,
    length=None,
    quantity=1,
    total_length_meters=None,
    price_per_sqm,
):
    """Mavjud xarid hujjatiga yangi qator qo'shadi va hujjat summalarini qayta hisoblaydi."""
    from .supplier_purchase import recalculate_totals

    with transaction.atomic():
        resolved_product_party = resolve_product_party(
            warehouse=purchase.warehouse,
            product_party=product_party,
            product_party_data=product_party_data,
        )
        subtotal = compute_subtotal(
            width=width,
            length=length,
            total_length_meters=total_length_meters,
            quantity=quantity,
            price_per_sqm=price_per_sqm,
        )
        item = SupplierPurchaseItem.objects.create(
            purchase=purchase,
            product_party=resolved_product_party,
            roll_number=roll_number,
            width=width,
            length=length,
            quantity=quantity if quantity is not None else 1,
            total_length_meters=total_length_meters,
            price_per_sqm=price_per_sqm,
            subtotal=subtotal,
        )
        recalculate_totals(purchase)

    return item


def update_purchase_item(item, **fields):
    """Qatorni yangilaydi, `subtotal`ni qayta hisoblaydi va hujjat summalarini yangilaydi."""
    from .supplier_purchase import recalculate_totals

    with transaction.atomic():
        for field_name, value in fields.items():
            setattr(item, field_name, value)

        item.subtotal = compute_subtotal(
            width=item.width,
            length=item.length,
            total_length_meters=item.total_length_meters,
            quantity=item.quantity,
            price_per_sqm=item.price_per_sqm,
        )
        item.save()
        recalculate_totals(item.purchase)

    return item


def delete_purchase_item(item):
    """Qatorni (soft-delete) o'chiradi va hujjat summalarini qayta hisoblaydi."""
    from .supplier_purchase import recalculate_totals

    purchase = item.purchase
    with transaction.atomic():
        item.delete()
        recalculate_totals(purchase)
