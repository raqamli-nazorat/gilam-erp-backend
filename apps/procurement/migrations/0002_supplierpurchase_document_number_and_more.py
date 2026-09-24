import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def backfill_document_numbers(apps, schema_editor):
    """Mavjud xarid hujjatlariga tashkilot bo'yicha ketma-ket raqam beradi."""
    SupplierPurchase = apps.get_model("procurement", "SupplierPurchase")

    counters = {}
    purchases = SupplierPurchase.objects.order_by("organization_id", "created_at")
    for purchase in purchases:
        counters[purchase.organization_id] = (
            counters.get(purchase.organization_id, 0) + 1
        )
        purchase.document_number = f"KR-{counters[purchase.organization_id]:04d}"
        purchase.save(update_fields=["document_number"])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("procurement", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="supplierpurchase",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="supplier_purchases_created",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Muallif",
            ),
        ),
        migrations.AddField(
            model_name="supplierpurchase",
            name="status",
            field=models.CharField(
                choices=[("draft", "Qoralama"), ("confirmed", "Tasdiqlangan")],
                db_index=True,
                default="draft",
                max_length=20,
                verbose_name="Holat",
            ),
        ),
        migrations.AddField(
            model_name="supplierpurchase",
            name="document_number",
            field=models.CharField(
                blank=True,
                default="",
                editable=False,
                max_length=20,
                verbose_name="Hujjat raqami",
            ),
        ),
        migrations.RunPython(backfill_document_numbers, noop_reverse),
        migrations.AlterField(
            model_name="supplierpurchase",
            name="document_number",
            field=models.CharField(
                editable=False,
                max_length=20,
                unique=True,
                verbose_name="Hujjat raqami",
            ),
        ),
    ]
