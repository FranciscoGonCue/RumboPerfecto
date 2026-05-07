"""
Añade campos de disponibilidad (fecha_disponible_desde, fecha_disponible_hasta,
fechas_no_disponibles) a DetalleActividad y DetalleRestauracion,
y turnos_disponibles a DetalleRestauracion.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketdata', '0004_new_fields'),
    ]

    operations = [
        # ── DetalleActividad ──────────────────────────────────────────────
        migrations.AddField(
            model_name='detalleactividad',
            name='fecha_disponible_desde',
            field=models.DateField(blank=True, null=True, verbose_name='Disponible desde'),
        ),
        migrations.AddField(
            model_name='detalleactividad',
            name='fecha_disponible_hasta',
            field=models.DateField(blank=True, null=True, verbose_name='Disponible hasta'),
        ),
        migrations.AddField(
            model_name='detalleactividad',
            name='fechas_no_disponibles',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='Fechas no disponibles (JSON)'),
        ),
        # ── DetalleRestauracion ───────────────────────────────────────────
        migrations.AddField(
            model_name='detallerestauracion',
            name='fecha_disponible_desde',
            field=models.DateField(blank=True, null=True, verbose_name='Disponible desde'),
        ),
        migrations.AddField(
            model_name='detallerestauracion',
            name='fecha_disponible_hasta',
            field=models.DateField(blank=True, null=True, verbose_name='Disponible hasta'),
        ),
        migrations.AddField(
            model_name='detallerestauracion',
            name='fechas_no_disponibles',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='Fechas no disponibles (JSON)'),
        ),
        migrations.AddField(
            model_name='detallerestauracion',
            name='turnos_disponibles',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='Turnos disponibles (JSON)'),
        ),
    ]
