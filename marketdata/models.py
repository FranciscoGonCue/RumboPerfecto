from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Count


class TipoServicio(models.Model):
    id_tipo = models.AutoField(primary_key=True)
    nombre_tipo = models.TextField(null=True, blank=True)
    icono = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'TIPOS_SERVICIO'

    def __str__(self):
        return self.nombre_tipo or f"Tipo {self.id_tipo}"


class CatalogoServicio(models.Model):
    id_servicio = models.CharField(max_length=64, primary_key=True)
    tipo = models.ForeignKey(
        TipoServicio,
        on_delete=models.CASCADE,
        db_column='id_tipo',
        related_name='servicios',
        null=True,
        blank=True,
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='servicios',
        verbose_name='Usuario propietario',
    )
    nombre = models.TextField(null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    precio_base = models.FloatField(null=True, blank=True)
    ubicacion_lat = models.FloatField(null=True, blank=True)
    ubicacion_lon = models.FloatField(null=True, blank=True)
    imagen_url = models.TextField(null=True, blank=True)
    disponible = models.BooleanField(null=True, blank=True)

    # Campos nuevos (comunes a todas las vistas)
    valoracion = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True, verbose_name='Valoración (0-5)')
    num_resenas = models.IntegerField(null=True, blank=True, verbose_name='Nº reseñas')
    ciudad = models.CharField(max_length=120, null=True, blank=True)
    pais = models.CharField(max_length=100, null=True, blank=True)
    direccion = models.CharField(max_length=255, null=True, blank=True, verbose_name='Dirección')
    moneda = models.CharField(max_length=5, null=True, blank=True, default='€')
    etiquetas = models.JSONField(null=True, blank=True, default=list, verbose_name='Etiquetas (JSON)')
    destacado = models.BooleanField(default=False, verbose_name='Destacado')

    class Meta:
        db_table = 'CATALOGO_SERVICIOS'

    def __str__(self):
        return self.nombre or self.id_servicio


class ResenaServicio(models.Model):
    """
    Reseña de un usuario sobre un servicio del catálogo.
    Un usuario solo puede tener una reseña por servicio (unique constraint).
    """

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resenas_servicios',
        verbose_name='Usuario',
    )
    servicio = models.ForeignKey(
        CatalogoServicio,
        on_delete=models.CASCADE,
        related_name='resenas',
        db_column='id_servicio',
        verbose_name='Servicio',
    )
    mensaje = models.TextField(verbose_name='Mensaje')
    puntuacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Puntuación (1–5)',
    )
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

    class Meta:
        db_table = 'RESENAS_SERVICIO'
        ordering = ['-creado_en']
        verbose_name = 'Reseña de servicio'
        verbose_name_plural = 'Reseñas de servicios'
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'servicio'],
                name='uniq_resena_usuario_servicio',
            ),
        ]

    def __str__(self):
        return f'Reseña {self.pk} — {self.servicio_id} ({self.puntuacion}★)'

    @classmethod
    def sincronizar_valoracion_catalogo(cls, servicio_id: str) -> None:
        agg = cls.objects.filter(servicio_id=servicio_id).aggregate(
            promedio=Avg('puntuacion'),
            total=Count('id'),
        )
        promedio = agg['promedio']
        total = agg['total'] or 0
        if promedio is not None:
            valoracion = Decimal(str(round(float(promedio), 1)))
        else:
            valoracion = None
        CatalogoServicio.objects.filter(pk=servicio_id).update(
            valoracion=valoracion,
            num_resenas=total,
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        type(self).sincronizar_valoracion_catalogo(self.servicio_id)

    def delete(self, *args, **kwargs):
        sid = self.servicio_id
        super().delete(*args, **kwargs)
        type(self).sincronizar_valoracion_catalogo(sid)


class DetalleAlojamiento(models.Model):
    servicio = models.OneToOneField(
        CatalogoServicio,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='id_servicio',
        related_name='detalle_alojamiento',
    )
    estrellas = models.IntegerField(null=True, blank=True)
    hora_checkin = models.TimeField(null=True, blank=True)
    hora_checkout = models.TimeField(null=True, blank=True)
    amenidades = models.JSONField(null=True, blank=True, default=list, verbose_name='Amenities (JSON)')
    fecha_disponible_desde = models.DateField(null=True, blank=True, verbose_name='Disponible desde')
    fecha_disponible_hasta = models.DateField(null=True, blank=True, verbose_name='Disponible hasta')
    fechas_no_disponibles = models.JSONField(null=True, blank=True, default=list, verbose_name='Fechas no disponibles (JSON)')

    class Meta:
        db_table = 'DETALLE_ALOJAMIENTO'
        verbose_name = 'Alojamiento'
        verbose_name_plural = 'Alojamientos'

    def __str__(self):
        return self.servicio.nombre if self.servicio_id else "Alojamiento"


class DetalleTransporte(models.Model):
    servicio = models.OneToOneField(
        CatalogoServicio,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='id_servicio',
        related_name='detalle_transporte',
    )
    ciudad_origen = models.TextField(null=True, blank=True)
    ciudad_destino = models.TextField(null=True, blank=True)
    compania = models.TextField(null=True, blank=True)
    codigo_vuelo = models.TextField(null=True, blank=True)
    duracion_minutos = models.IntegerField(null=True, blank=True)
    # Campos nuevos
    asientos_disponibles = models.IntegerField(null=True, blank=True, verbose_name='Asientos disponibles')
    comodidades = models.JSONField(null=True, blank=True, default=list, verbose_name='Comodidades (JSON)')
    horarios_salida = models.JSONField(null=True, blank=True, default=list, verbose_name='Horarios de salida (JSON)')
    clases = models.JSONField(null=True, blank=True, default=list, verbose_name='Clases (JSON)')

    class Meta:
        db_table = 'DETALLE_TRANSPORTE'
        verbose_name = 'Transporte'
        verbose_name_plural = 'Transportes'

    def __str__(self):
        return self.servicio.nombre if self.servicio_id else "Transporte"


class DetalleRestauracion(models.Model):
    servicio = models.OneToOneField(
        CatalogoServicio,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='id_servicio',
        related_name='detalle_restauracion',
    )
    tipo_cocina = models.TextField(null=True, blank=True)
    es_vegano = models.BooleanField(null=True, blank=True)
    precio_medio = models.FloatField(null=True, blank=True)
    requiere_reserva = models.BooleanField(null=True, blank=True)
    rango_precios = models.CharField(max_length=5, null=True, blank=True, verbose_name='Rango de precios (€/€€/€€€)')
    abierto_ahora = models.BooleanField(null=True, blank=True, verbose_name='Abierto ahora')
    especialidades = models.JSONField(null=True, blank=True, default=list, verbose_name='Especialidades (JSON)')
    horario = models.JSONField(null=True, blank=True, default=dict, verbose_name='Horario semanal (JSON)')
    ubicacion_texto = models.CharField(max_length=255, null=True, blank=True, verbose_name='Dirección/zona')
    fecha_disponible_desde = models.DateField(null=True, blank=True, verbose_name='Disponible desde')
    fecha_disponible_hasta = models.DateField(null=True, blank=True, verbose_name='Disponible hasta')
    fechas_no_disponibles = models.JSONField(null=True, blank=True, default=list, verbose_name='Fechas no disponibles (JSON)')
    turnos_disponibles = models.JSONField(null=True, blank=True, default=list, verbose_name='Turnos disponibles (JSON)')
    # Por cada fecha (YYYY-MM-DD), lista de turnos ya reservados (no modificar turnos_disponibles plantilla)
    turnos_ocupados = models.JSONField(null=True, blank=True, default=dict, verbose_name='Turnos ocupados por fecha (JSON)')

    class Meta:
        db_table = 'DETALLE_RESTAURACION'
        verbose_name = 'Restauración'
        verbose_name_plural = 'Restauraciones'

    def __str__(self):
        return self.servicio.nombre if self.servicio_id else "Restauración"


DIFICULTAD_CHOICES = [
    ('Fácil', 'Fácil'),
    ('Moderado', 'Moderado'),
    ('Difícil', 'Difícil'),
    ('Extremo', 'Extremo'),
]


class DetalleActividad(models.Model):
    servicio = models.OneToOneField(
        CatalogoServicio,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='id_servicio',
        related_name='detalle_actividad',
    )
    duracion_estimada = models.IntegerField(null=True, blank=True, verbose_name='Duración (minutos)')
    aforo_maximo = models.IntegerField(null=True, blank=True, verbose_name='Aforo máximo')
    horario_apertura = models.TextField(null=True, blank=True)
    guia_incluido = models.BooleanField(null=True, blank=True)
    # Campos nuevos
    dificultad = models.CharField(max_length=20, choices=DIFICULTAD_CHOICES, null=True, blank=True)
    duracion_texto = models.CharField(max_length=50, null=True, blank=True, verbose_name='Duración (texto, ej: "2h 30m")')
    ubicacion_texto = models.CharField(max_length=255, null=True, blank=True, verbose_name='Ubicación/zona')
    incluye = models.JSONField(null=True, blank=True, default=list, verbose_name='Incluye (JSON)')
    requisitos = models.JSONField(null=True, blank=True, default=list, verbose_name='Requisitos (JSON)')
    turnos_disponibles = models.JSONField(null=True, blank=True, default=list, verbose_name='Turnos disponibles (JSON)')
    fecha_disponible_desde = models.DateField(null=True, blank=True, verbose_name='Disponible desde')
    fecha_disponible_hasta = models.DateField(null=True, blank=True, verbose_name='Disponible hasta')
    fechas_no_disponibles = models.JSONField(null=True, blank=True, default=list, verbose_name='Fechas no disponibles (JSON)')
    turnos_ocupados = models.JSONField(null=True, blank=True, default=dict, verbose_name='Turnos ocupados por fecha (JSON)')

    class Meta:
        db_table = 'DETALLE_ACTIVIDAD'
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

    def __str__(self):
        return self.servicio.nombre if self.servicio_id else "Actividad"
