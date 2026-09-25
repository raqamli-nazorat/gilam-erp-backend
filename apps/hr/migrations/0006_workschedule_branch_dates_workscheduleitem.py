import datetime
import uuid

import django.db.models.deletion
from django.db import migrations, models


def clear_work_schedules(apps, schema_editor):
    """Eski `days` asosidagi ish grafiklarini o'chiradi — yangi maydonlar majburiy (branch, sanalar)."""
    apps.get_model("hr", "WorkSchedule").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        (
            "organization",
            "0002_alter_branch_options_alter_organization_options_and_more",
        ),
        ("hr", "0005_remove_workschedule_is_friday_and_more"),
    ]

    operations = [
        migrations.RunPython(clear_work_schedules, migrations.RunPython.noop),
        migrations.RemoveField(model_name="recruitmentdismissal", name="attachment"),
        migrations.RemoveField(model_name="workschedule", name="days"),
        migrations.AddField(
            model_name="workschedule",
            name="branch",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="work_schedules",
                to="organization.branch",
                verbose_name="Filial",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="workschedule",
            name="from_date",
            field=models.DateField(
                default=datetime.date(2026, 1, 1), verbose_name="Boshlanish sanasi"
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="workschedule",
            name="to_date",
            field=models.DateField(
                default=datetime.date(2026, 1, 1), verbose_name="Tugash sanasi"
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="WorkScheduleItem",
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
                ("name", models.CharField(max_length=100, verbose_name="Nomi")),
                (
                    "day_type",
                    models.CharField(
                        choices=[
                            ("full_holiday", "To'liq bayram"),
                            ("partial_workday", "Qisman ish kuni"),
                            ("full_workday", "To'liq ish kuni"),
                        ],
                        db_index=True,
                        max_length=20,
                        verbose_name="Kun turi",
                    ),
                ),
                ("day_date", models.DateField(verbose_name="Sana")),
                ("from_hour", models.TimeField(verbose_name="Boshlanish vaqti")),
                ("to_hour", models.TimeField(verbose_name="Tugash vaqti")),
                (
                    "work_schedule",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="hr.workschedule",
                        verbose_name="Ish grafigi",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ish grafigi kuni",
                "verbose_name_plural": "Ish grafigi kunlari",
                "db_table": "hr_work_schedule_item",
            },
        ),
    ]
