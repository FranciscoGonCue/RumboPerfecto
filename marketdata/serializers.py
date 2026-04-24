from rest_framework import serializers
from .models import (
    TipoServicio, CatalogoServicio,
    DetalleAlojamiento, DetalleTransporte,
    DetalleRestauracion, DetalleActividad,
)


class TipoServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoServicio
        fields = ["id_tipo", "nombre_tipo", "icono"]


class DetalleAlojamientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleAlojamiento
        fields = ["estrellas", "hora_checkin", "hora_checkout", "servicios_extra"]


class DetalleTransporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleTransporte
        fields = ["ciudad_origen", "ciudad_destino", "compania", "codigo_vuelo", "duracion_minutos"]


class DetalleRestauracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleRestauracion
        fields = ["tipo_cocina", "es_vegano", "precio_medio", "requiere_reserva"]


class DetalleActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleActividad
        fields = ["duracion_estimada", "aforo_maximo", "horario_apertura", "guia_incluido"]


class CatalogoServicioSerializer(serializers.ModelSerializer):
    tipo = TipoServicioSerializer(read_only=True)
    detalle_alojamiento = DetalleAlojamientoSerializer(read_only=True, default=None)
    detalle_transporte = DetalleTransporteSerializer(read_only=True, default=None)
    detalle_restauracion = DetalleRestauracionSerializer(read_only=True, default=None)
    detalle_actividad = DetalleActividadSerializer(read_only=True, default=None)

    class Meta:
        model = CatalogoServicio
        fields = [
            "id_servicio", "tipo", "nombre", "descripcion",
            "precio_base", "ubicacion_lat", "ubicacion_lon",
            "imagen_url", "disponible",
            "detalle_alojamiento", "detalle_transporte",
            "detalle_restauracion", "detalle_actividad",
        ]
