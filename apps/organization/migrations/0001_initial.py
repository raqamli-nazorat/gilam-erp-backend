import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Country",
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
                "verbose_name": "Davlat",
                "verbose_name_plural": "Davlatlar",
                "db_table": "organization_country",
            },
        ),
        migrations.CreateModel(
            name="District",
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
                "verbose_name": "Tuman",
                "verbose_name_plural": "Tumanlar",
                "db_table": "organization_district",
            },
        ),
        migrations.CreateModel(
            name="Region",
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
                    "country",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="regions",
                        to="organization.country",
                        verbose_name="Davlat",
                    ),
                ),
            ],
            options={
                "verbose_name": "Viloyat",
                "verbose_name_plural": "Viloyatlar",
                "db_table": "organization_region",
            },
        ),
        migrations.CreateModel(
            name="Organization",
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
                    "inn",
                    models.CharField(max_length=20, unique=True, verbose_name="INN"),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True, default="", max_length=50, verbose_name="Telefon"
                    ),
                ),
                (
                    "director",
                    models.CharField(
                        blank=True, default="", max_length=50, verbose_name="Rahbar"
                    ),
                ),
                (
                    "address",
                    models.TextField(blank=True, default="", verbose_name="Manzil"),
                ),
                (
                    "prefix",
                    models.CharField(
                        blank=True, default="", max_length=255, verbose_name="Prefiks"
                    ),
                ),
                (
                    "district",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="organizations",
                        to="organization.district",
                        verbose_name="Tuman",
                    ),
                ),
                (
                    "region",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="organizations",
                        to="organization.region",
                        verbose_name="Viloyat",
                    ),
                ),
            ],
            options={
                "verbose_name": "Tashkilot",
                "verbose_name_plural": "Tashkilotlar",
                "db_table": "organization_organization",
            },
        ),
        migrations.AddField(
            model_name="district",
            name="region",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="districts",
                to="organization.region",
                verbose_name="Viloyat",
            ),
        ),
        migrations.CreateModel(
            name="Branch",
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
                    "phone",
                    models.CharField(
                        blank=True, default="", max_length=50, verbose_name="Telefon"
                    ),
                ),
                (
                    "address",
                    models.TextField(blank=True, default="", verbose_name="Manzil"),
                ),
                (
                    "district",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="branches",
                        to="organization.district",
                        verbose_name="Tuman",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="branches",
                        to="organization.organization",
                        verbose_name="Tashkilot",
                    ),
                ),
                (
                    "region",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="branches",
                        to="organization.region",
                        verbose_name="Viloyat",
                    ),
                ),
            ],
            options={
                "verbose_name": "Filial",
                "verbose_name_plural": "Filiallar",
                "db_table": "organization_branch",
            },
        ),
    ]
