from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0003_remove_itemplan_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemplan',
            name='localizador_confirmacion',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='itemplan',
            name='estado_pago',
            field=models.CharField(
                blank=True,
                choices=[('Pendiente', 'Pendiente'), ('Pagado', 'Pagado'), ('Cancelado', 'Cancelado')],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='itemplan',
            name='monto_total',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='itemplan',
            name='fecha_transaccion',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='Reserva',
        ),
    ]
