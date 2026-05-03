from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_rename_service_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='planings',
            field=models.JSONField(blank=True, default=list, verbose_name='Plannings'),
        ),
    ]
