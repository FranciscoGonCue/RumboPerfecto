from django.conf import settings
from django.db import models


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

    class Meta:
        db_table = 'CATALOGO_SERVICIOS'

    def __str__(self):
        return self.nombre or self.id_servicio


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
    servicios_extra = models.TextField(null=True, blank=True)

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

    class Meta:
        db_table = 'DETALLE_RESTAURACION'
        verbose_name = 'Restauración'
        verbose_name_plural = 'Restauraciones'

    def __str__(self):
        return self.servicio.nombre if self.servicio_id else "Restauración"


class DetalleActividad(models.Model):
    servicio = models.OneToOneField(
        CatalogoServicio,
        on_delete=models.CASCADE,
        primary_key=True,
        db_column='id_servicio',
        related_name='detalle_actividad',
    )
    duracion_estimada = models.IntegerField(null=True, blank=True)
    aforo_maximo = models.IntegerField(null=True, blank=True)
    horario_apertura = models.TextField(null=True, blank=True)
    guia_incluido = models.BooleanField(null=True, blank=True)

    class Meta:
        db_table = 'DETALLE_ACTIVIDAD'
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

    def __str__(self):
        return self.servicio.nombre if self.servicio_id else "Actividad"
