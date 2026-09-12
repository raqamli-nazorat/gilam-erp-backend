import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('hr', '0001_initial'),
        ('organization', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='role',
            name='is_system',
            field=models.BooleanField(default=False, help_text="O'chirib bo'lmaydigan asosiy rol (masalan, dastlabki Admin roli)", verbose_name='Tizim roli'),
        ),
        migrations.AddField(
            model_name='role',
            name='organization',
            field=models.ForeignKey(blank=True, help_text="NULL bo'lsa tizim darajasidagi rol (masalan: Super Admin)", null=True, on_delete=django.db.models.deletion.CASCADE, related_name='roles', to='organization.organization', verbose_name='Tashkilot'),
        ),
        migrations.AddField(
            model_name='role',
            name='permissions',
            field=models.ManyToManyField(blank=True, related_name='custom_roles', to='auth.permission', verbose_name='Huquqlar'),
        ),
        migrations.AddField(
            model_name='user',
            name='all_branches',
            field=models.BooleanField(default=False, help_text='Tashkilotning barcha filiallarini boshqara olish huquqi', verbose_name='Barcha filiallar'),
        ),
        migrations.AddField(
            model_name='user',
            name='employee',
            field=models.OneToOneField(blank=True, help_text='Biriktirilgan kadrlar xodimi', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_account', to='hr.employee', verbose_name='Xodim'),
        ),
        migrations.AddField(
            model_name='user',
            name='organization',
            field=models.ForeignKey(blank=True, help_text="NULL bo'lsa tizim darajasidagi foydalanuvchi (Super Admin)", null=True, on_delete=django.db.models.deletion.PROTECT, related_name='users', to='organization.organization', verbose_name='Tashkilot'),
        ),
    ]
