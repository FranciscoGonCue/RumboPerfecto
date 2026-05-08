import django.db.models.deletion
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('marketdata', '0006_turnos_ocupados'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResenaServicio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mensaje', models.TextField(verbose_name='Mensaje')),
                (
                    'puntuacion',
                    models.PositiveSmallIntegerField(
                        validators=[MinValueValidator(1), MaxValueValidator(5)],
                        verbose_name='Puntuación (1–5)',
                    ),
                ),
                ('creado_en', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')),
                (
                    'servicio',
                    models.ForeignKey(
                        db_column='id_servicio',
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='resenas',
                        to='marketdata.catalogoservicio',
                        verbose_name='Servicio',
                    ),
                ),
                (
                    'usuario',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='resenas_servicios',
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='Usuario',
                    ),
                ),
            ],
            options={
                'verbose_name': 'Reseña de servicio',
                'verbose_name_plural': 'Reseñas de servicios',
                'db_table': 'RESENAS_SERVICIO',
                'ordering': ['-creado_en'],
            },
        ),
        migrations.AddConstraint(
            model_name='resenaservicio',
            constraint=models.UniqueConstraint(
                fields=('usuario', 'servicio'),
                name='uniq_resena_usuario_servicio',
            ),
        ),
    ]
