from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0006_itemplan_reserva'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemplan',
            name='ubicacion_direccion',
            field=models.TextField(blank=True, null=True, verbose_name='Dirección (mapa)'),
        ),
    ]
