import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CounterpartyType",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        db_index=True, default=True, verbose_name="Is Active"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
                        verbose_name="Yaratilgan vaqti",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Yangilangan vaqti"
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Nomi")),
            ],
            options={
                "verbose_name": "Kontragent turi",
                "verbose_name_plural": "Kontragent turlari",
                "db_table": "finance_counterparty_type",
            },
        ),
        migrations.CreateModel(
            name="Currency",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        db_index=True, default=True, verbose_name="Is Active"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
                        verbose_name="Yaratilgan vaqti",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Yangilangan vaqti"
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Nomi")),
                (
                    "short_name",
                    models.CharField(max_length=255, verbose_name="Qisqa nomi"),
                ),
            ],
            options={
                "verbose_name": "Valyuta",
                "verbose_name_plural": "Valyutalar",
                "db_table": "finance_currency",
            },
        ),
        migrations.CreateModel(
            name="Counterparty",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        db_index=True, default=True, verbose_name="Is Active"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
                        verbose_name="Yaratilgan vaqti",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Yangilangan vaqti"
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Nomi")),
                (
                    "phone_number",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=50,
                        verbose_name="Telefon raqami",
                    ),
                ),
                (
                    "type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="counterparties",
                        to="finance.counterpartytype",
                        verbose_name="Turi",
                    ),
                ),
            ],
            options={
                "verbose_name": "Kontragent",
                "verbose_name_plural": "Kontragentlar",
                "db_table": "finance_counterparty",
            },
        ),
        migrations.CreateModel(
            name="AccrualRetention",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        db_index=True, default=True, verbose_name="Is Active"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
                        verbose_name="Yaratilgan vaqti",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Yangilangan vaqti"
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Nomi")),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("percent", "Foiz"),
                            ("fix_summa", "Belgilangan summa"),
                        ],
                        db_index=True,
                        max_length=20,
                        verbose_name="Turi",
                    ),
                ),
                (
                    "value",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=15,
                        verbose_name="Qiymati",
                    ),
                ),
                (
                    "currency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="accrual_retentions",
                        to="finance.currency",
                        verbose_name="Valyuta",
                    ),
                ),
            ],
            options={
                "verbose_name": "Hisoblash / ushlab qolish",
                "verbose_name_plural": "Hisoblash / ushlab qolishlar",
                "db_table": "finance_accrual_retention",
            },
        ),
        migrations.CreateModel(
            name="CurrencyLedger",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        db_index=True, default=True, verbose_name="Is Active"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
                        verbose_name="Yaratilgan vaqti",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Yangilangan vaqti"
                    ),
                ),
                (
                    "value",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=15,
                        verbose_name="Qiymati",
                    ),
                ),
                ("day", models.DateField(verbose_name="Sana")),
                (
                    "currency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="ledgers",
                        to="finance.currency",
                        verbose_name="Valyuta",
                    ),
                ),
            ],
            options={
                "verbose_name": "Valyuta kursi",
                "verbose_name_plural": "Valyuta kurslari",
                "db_table": "finance_currency_ledger",
            },
        ),
    ]
