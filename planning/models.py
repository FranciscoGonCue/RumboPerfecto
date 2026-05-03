from django.db import models
from django.conf import settings
from marketdata.models import TipoServicio


class EstadoPlan(models.TextChoices):
    BORRADOR = 'Borrador', 'Borrador'
    CONFIRMADO = 'Confirmado', 'Confirmado'
    FINALIZADO = 'Finalizado', 'Finalizado'


class EstadoPago(models.TextChoices):
    PENDIENTE = 'Pendiente', 'Pendiente'
    PAGADO = 'Pagado', 'Pagado'
    CANCELADO = 'Cancelado', 'Cancelado'


class PlanViaje(models.Model):
    id_plan = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_column='id_usuario',
        related_name='planes_viaje',
        null=True,
        blank=True,
    )
    nombre_plan = models.TextField(null=True, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    estado_plan = models.CharField(max_length=20, choices=EstadoPlan.choices, null=True, blank=True)

    class Meta:
        db_table = 'PLANES_VIAJE'

    def __str__(self):
        return self.nombre_plan or f"Plan {self.id_plan}"


class ItemPlan(models.Model):
    id_item = models.AutoField(primary_key=True)
    plan = models.ForeignKey(
        PlanViaje,
        on_delete=models.CASCADE,
        db_column='id_plan',
        related_name='items',
        null=True,
        blank=True,
    )
    tipo = models.ForeignKey(
        TipoServicio,
        on_delete=models.CASCADE,
        db_column='id_tipo',
        related_name='items',
        null=True,
        blank=True,
    )
    nombre_servicio = models.TextField(null=True, blank=True)
    ubicacion_lat = models.FloatField(null=True, blank=True)
    ubicacion_lon = models.FloatField(null=True, blank=True)
    fecha_hora_inicio = models.DateTimeField(null=True, blank=True)
    fecha_hora_fin = models.DateTimeField(null=True, blank=True)
    precio_estimado = models.FloatField(null=True, blank=True)
    localizador_confirmacion = models.TextField(null=True, blank=True)
    estado_pago = models.CharField(max_length=20, choices=EstadoPago.choices, null=True, blank=True)
    monto_total = models.FloatField(null=True, blank=True)
    fecha_transaccion = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ITEMS_PLAN'

    def save(self, *args, **kwargs):
        # Rellenar monto_total con precio_estimado si no se ha indicado explícitamente
        if self.monto_total is None and self.precio_estimado is not None:
            self.monto_total = self.precio_estimado
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre_servicio or f"Item {self.id_item}"
