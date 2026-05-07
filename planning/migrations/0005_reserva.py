from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('planning', '0004_merge_reserva_into_itemplan'),
        ('marketdata', '0005_availability_act_rest'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_inicio', models.DateField(verbose_name='Fecha inicio / check-in')),
                ('fecha_fin', models.DateField(blank=True, null=True, verbose_name='Fecha fin / check-out')),
                ('turno', models.CharField(blank=True, max_length=10, null=True, verbose_name='Turno (hora)')),
                ('personas', models.PositiveIntegerField(default=1, verbose_name='Nº personas')),
                ('precio_total', models.FloatField(blank=True, null=True, verbose_name='Precio total')),
                ('estado', models.CharField(
                    choices=[('Pendiente', 'Pendiente'), ('Confirmada', 'Confirmada'), ('Cancelada', 'Cancelada')],
                    default='Pendiente',
                    max_length=20,
                    verbose_name='Estado',
                )),
                ('notas', models.TextField(blank=True, null=True, verbose_name='Notas')),
                ('creado_en', models.DateTimeField(auto_now_add=True, verbose_name='Creado en')),
                ('usuario', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reservas',
                    to=settings.AUTH_USER_MODEL,
                    verbose_name='Usuario',
                )),
                ('servicio', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='reservas',
                    to='marketdata.catalogoservicio',
                    verbose_name='Servicio',
                )),
            ],
            options={
                'verbose_name': 'Reserva',
                'verbose_name_plural': 'Reservas',
                'db_table': 'RESERVAS',
                'ordering': ['-creado_en'],
            },
        ),
    ]
