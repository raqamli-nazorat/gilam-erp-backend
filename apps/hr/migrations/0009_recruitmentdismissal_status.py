from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("hr", "0008_workschedule_work_days_choices")]

    operations = [
        migrations.AddField(
            model_name="recruitmentdismissal",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Qoralama"),
                    ("approved", "Tasdiqlangan"),
                    ("cancelled", "Bekor qilingan"),
                ],
                db_index=True,
                default="approved",
                max_length=20,
                verbose_name="Holati",
            ),
        ),
    ]
