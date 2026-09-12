import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("organization", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Warehouse",
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
                    "address",
                    models.TextField(blank=True, default="", verbose_name="Manzil"),
                ),
                (
                    "branch",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="warehouses",
                        to="organization.branch",
                        verbose_name="Filial",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ombor",
                "verbose_name_plural": "Omborlar",
                "db_table": "warehouse_warehouse",
            },
        ),
    ]
