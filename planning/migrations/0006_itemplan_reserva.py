import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0005_reserva'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemplan',
            name='reserva',
            field=models.OneToOneField(
                blank=True,
                db_column='id_reserva',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='item_plan',
                to='planning.reserva',
                verbose_name='Reserva de origen',
            ),
        ),
    ]
