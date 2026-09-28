import apps.utils.validators
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hr", "0011_employeeledger_date_calculatingsalary"),
    ]

    operations = [
        migrations.AddField(
            model_name="calculatingsalary",
            name="cancel_reason",
            field=models.TextField(
                blank=True, default="", verbose_name="Bekor qilish sababi"
            ),
        ),
        migrations.AddField(
            model_name="calculatingsalary",
            name="cancel_attachment",
            field=models.FileField(
                blank=True,
                help_text="Bekor qilish asosi (PDF yoki Excel, 10 MB gacha)",
                null=True,
                upload_to="hr/calculating_salaries/cancel/%Y/%m/",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        ["pdf", "xls", "xlsx"],
                        message="Faqat PDF yoki Excel (XLS, XLSX) fayl yuklash mumkin.",
                    ),
                    apps.utils.validators.FileSizeValidator(max_size_mb=10),
                ],
                verbose_name="Bekor qilish hujjati",
            ),
        ),
    ]
