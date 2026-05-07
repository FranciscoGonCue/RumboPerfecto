from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketdata', '0005_availability_act_rest'),
    ]

    operations = [
        migrations.AddField(
            model_name='detalleactividad',
            name='turnos_ocupados',
            field=models.JSONField(blank=True, default=dict, null=True, verbose_name='Turnos ocupados por fecha (JSON)'),
        ),
        migrations.AddField(
            model_name='detallerestauracion',
            name='turnos_ocupados',
            field=models.JSONField(blank=True, default=dict, null=True, verbose_name='Turnos ocupados por fecha (JSON)'),
        ),
    ]
