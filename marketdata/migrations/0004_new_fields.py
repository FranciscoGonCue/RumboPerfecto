"""
Migración manual que sincroniza el estado Django con la BD real.

Situación de la BD antes de esta migración:
  - Todos los campos nuevos (ciudad, valoracion, dificultad, etc.) YA ESTÁN en la BD
    (aplicados parcialmente por migraciones fallidas anteriores).
  - servicios_extra YA FUE ELIMINADO de DETALLE_ALOJAMIENTO.
  - amenidades NO está todavía en la BD.

Por eso usamos SeparateDatabaseAndState:
  - state_operations: refleja TODOS los cambios para que Django
    sincronice su estado interno con el modelo actual.
  - database_operations: solo ejecuta el ADD COLUMN amenidades,
    que es lo único que falta en la BD.
"""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketdata', '0003_alter_detalleactividad_options_and_more'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # ── CatalogoServicio ──────────────────────────────────────
                migrations.AddField(
                    model_name='catalogoservicio',
                    name='ciudad',
                    field=models.CharField(blank=True, max_length=120, null=True),
                ),
                migrations.AddField(
                    model_name='catalogoservicio',
                    name='destacado',
                    field=models.BooleanField(default=False, verbose_name='Destacado'),
                ),
                migrations.AddField(
                    model_name='catalogoservicio',
                    name='direccion',
                    field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Dirección'),
                ),
                migrations.AddField(
                    model_name='catalogoservicio',
                    name='etiquetas',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Etiquetas (JSON)'),
                ),
                migrations.AddField(
                    model_name='catalogoservicio',
                    name='moneda',
                    field=models.CharField(blank=True, default='€', max_length=5, null=True),
                ),
                migrations.AddField(
                    model_name='catalogoservicio',
                    name='num_resenas',
                    field=models.IntegerField(blank=True, null=True, verbose_name='Nº reseñas'),
                ),
                migrations.AddField(
                    model_name='catalogoservicio',
                    name='pais',
                    field=models.CharField(blank=True, max_length=100, null=True),
                ),
                migrations.AddField(
                    model_name='catalogoservicio',
                    name='valoracion',
                    field=models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True, verbose_name='Valoración (0-5)'),
                ),
                # ── DetalleActividad ──────────────────────────────────────
                migrations.AddField(
                    model_name='detalleactividad',
                    name='dificultad',
                    field=models.CharField(
                        blank=True, max_length=20, null=True,
                        choices=[('Fácil', 'Fácil'), ('Moderado', 'Moderado'), ('Difícil', 'Difícil'), ('Extremo', 'Extremo')],
                    ),
                ),
                migrations.AddField(
                    model_name='detalleactividad',
                    name='duracion_texto',
                    field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Duración (texto, ej: "2h 30m")'),
                ),
                migrations.AddField(
                    model_name='detalleactividad',
                    name='incluye',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Incluye (JSON)'),
                ),
                migrations.AddField(
                    model_name='detalleactividad',
                    name='requisitos',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Requisitos (JSON)'),
                ),
                migrations.AddField(
                    model_name='detalleactividad',
                    name='turnos_disponibles',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Turnos disponibles (JSON)'),
                ),
                migrations.AddField(
                    model_name='detalleactividad',
                    name='ubicacion_texto',
                    field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Ubicación/zona'),
                ),
                migrations.AlterField(
                    model_name='detalleactividad',
                    name='aforo_maximo',
                    field=models.IntegerField(blank=True, null=True, verbose_name='Aforo máximo'),
                ),
                migrations.AlterField(
                    model_name='detalleactividad',
                    name='duracion_estimada',
                    field=models.IntegerField(blank=True, null=True, verbose_name='Duración (minutos)'),
                ),
                # ── DetalleAlojamiento ────────────────────────────────────
                migrations.RemoveField(
                    model_name='detallealojamiento',
                    name='servicios_extra',
                ),
                migrations.AddField(
                    model_name='detallealojamiento',
                    name='amenidades',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Amenities (JSON)'),
                ),
                migrations.AddField(
                    model_name='detallealojamiento',
                    name='fecha_disponible_desde',
                    field=models.DateField(blank=True, null=True, verbose_name='Disponible desde'),
                ),
                migrations.AddField(
                    model_name='detallealojamiento',
                    name='fecha_disponible_hasta',
                    field=models.DateField(blank=True, null=True, verbose_name='Disponible hasta'),
                ),
                migrations.AddField(
                    model_name='detallealojamiento',
                    name='fechas_no_disponibles',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Fechas no disponibles (JSON)'),
                ),
                # ── DetalleRestauracion ───────────────────────────────────
                migrations.AddField(
                    model_name='detallerestauracion',
                    name='abierto_ahora',
                    field=models.BooleanField(blank=True, null=True, verbose_name='Abierto ahora'),
                ),
                migrations.AddField(
                    model_name='detallerestauracion',
                    name='especialidades',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Especialidades (JSON)'),
                ),
                migrations.AddField(
                    model_name='detallerestauracion',
                    name='horario',
                    field=models.JSONField(blank=True, default=dict, null=True, verbose_name='Horario semanal (JSON)'),
                ),
                migrations.AddField(
                    model_name='detallerestauracion',
                    name='rango_precios',
                    field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Rango de precios (€/€€/€€€)'),
                ),
                migrations.AddField(
                    model_name='detallerestauracion',
                    name='ubicacion_texto',
                    field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Dirección/zona'),
                ),
                # ── DetalleTransporte ─────────────────────────────────────
                migrations.AddField(
                    model_name='detalletransporte',
                    name='asientos_disponibles',
                    field=models.IntegerField(blank=True, null=True, verbose_name='Asientos disponibles'),
                ),
                migrations.AddField(
                    model_name='detalletransporte',
                    name='clases',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Clases (JSON)'),
                ),
                migrations.AddField(
                    model_name='detalletransporte',
                    name='comodidades',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Comodidades (JSON)'),
                ),
                migrations.AddField(
                    model_name='detalletransporte',
                    name='horarios_salida',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Horarios de salida (JSON)'),
                ),
            ],
            database_operations=[
                # ── CatalogoServicio ──────────────────────────────────────
                migrations.AddField(
                    model_name='catalogoservicio',
                    name='ciudad',
                    field=models.CharField(blank=True, max_length=120, null=True),
                ),
                migrations.AddField(
                    model_name='catalogoservicio',
                    name='destacado',
                    field=models.BooleanField(default=False, verbose_name='Destacado'),
                ),
                migrations.AddField(
                    model_name='catalogoservicio',
                    name='direccion',
                    field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Dirección'),
                ),
                migrations.AddField(
                    model_name='catalogoservicio',
                    name='etiquetas',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Etiquetas (JSON)'),
                ),
                migrations.AddField(
                    model_name='catalogoservicio',
                    name='moneda',
                    field=models.CharField(blank=True, default='€', max_length=5, null=True),
                ),
                migrations.AddField(
                    model_name='catalogoservicio',
                    name='num_resenas',
                    field=models.IntegerField(blank=True, null=True, verbose_name='Nº reseñas'),
                ),
                migrations.AddField(
                    model_name='catalogoservicio',
                    name='pais',
                    field=models.CharField(blank=True, max_length=100, null=True),
                ),
                migrations.AddField(
                    model_name='catalogoservicio',
                    name='valoracion',
                    field=models.DecimalField(blank=True, decimal_places=1, max_digits=3, null=True, verbose_name='Valoración (0-5)'),
                ),
                # ── DetalleActividad ──────────────────────────────────────
                migrations.AddField(
                    model_name='detalleactividad',
                    name='dificultad',
                    field=models.CharField(
                        blank=True, max_length=20, null=True,
                        choices=[('Fácil', 'Fácil'), ('Moderado', 'Moderado'), ('Difícil', 'Difícil'), ('Extremo', 'Extremo')],
                    ),
                ),
                migrations.AddField(
                    model_name='detalleactividad',
                    name='duracion_texto',
                    field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Duración (texto, ej: "2h 30m")'),
                ),
                migrations.AddField(
                    model_name='detalleactividad',
                    name='incluye',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Incluye (JSON)'),
                ),
                migrations.AddField(
                    model_name='detalleactividad',
                    name='requisitos',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Requisitos (JSON)'),
                ),
                migrations.AddField(
                    model_name='detalleactividad',
                    name='turnos_disponibles',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Turnos disponibles (JSON)'),
                ),
                migrations.AddField(
                    model_name='detalleactividad',
                    name='ubicacion_texto',
                    field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Ubicación/zona'),
                ),
                # ── DetalleAlojamiento ────────────────────────────────────
                migrations.RemoveField(
                    model_name='detallealojamiento',
                    name='servicios_extra',
                ),
                migrations.AddField(
                    model_name='detallealojamiento',
                    name='amenidades',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Amenities (JSON)'),
                ),
                migrations.AddField(
                    model_name='detallealojamiento',
                    name='fecha_disponible_desde',
                    field=models.DateField(blank=True, null=True, verbose_name='Disponible desde'),
                ),
                migrations.AddField(
                    model_name='detallealojamiento',
                    name='fecha_disponible_hasta',
                    field=models.DateField(blank=True, null=True, verbose_name='Disponible hasta'),
                ),
                migrations.AddField(
                    model_name='detallealojamiento',
                    name='fechas_no_disponibles',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Fechas no disponibles (JSON)'),
                ),
                # ── DetalleRestauracion ───────────────────────────────────
                migrations.AddField(
                    model_name='detallerestauracion',
                    name='abierto_ahora',
                    field=models.BooleanField(blank=True, null=True, verbose_name='Abierto ahora'),
                ),
                migrations.AddField(
                    model_name='detallerestauracion',
                    name='especialidades',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Especialidades (JSON)'),
                ),
                migrations.AddField(
                    model_name='detallerestauracion',
                    name='horario',
                    field=models.JSONField(blank=True, default=dict, null=True, verbose_name='Horario semanal (JSON)'),
                ),
                migrations.AddField(
                    model_name='detallerestauracion',
                    name='rango_precios',
                    field=models.CharField(blank=True, max_length=5, null=True, verbose_name='Rango de precios (€/€€/€€€)'),
                ),
                migrations.AddField(
                    model_name='detallerestauracion',
                    name='ubicacion_texto',
                    field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Dirección/zona'),
                ),
                # ── DetalleTransporte ─────────────────────────────────────
                migrations.AddField(
                    model_name='detalletransporte',
                    name='asientos_disponibles',
                    field=models.IntegerField(blank=True, null=True, verbose_name='Asientos disponibles'),
                ),
                migrations.AddField(
                    model_name='detalletransporte',
                    name='clases',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Clases (JSON)'),
                ),
                migrations.AddField(
                    model_name='detalletransporte',
                    name='comodidades',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Comodidades (JSON)'),
                ),
                migrations.AddField(
                    model_name='detalletransporte',
                    name='horarios_salida',
                    field=models.JSONField(blank=True, default=list, null=True, verbose_name='Horarios de salida (JSON)'),
                ),
            ],
        ),
    ]
