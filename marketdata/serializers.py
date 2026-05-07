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
        fields = [
            "estrellas", "hora_checkin", "hora_checkout",
            "amenidades",
            "fecha_disponible_desde", "fecha_disponible_hasta",
            "fechas_no_disponibles",
        ]


class DetalleTransporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleTransporte
        fields = [
            "ciudad_origen", "ciudad_destino", "compania",
            "codigo_vuelo", "duracion_minutos",
            "asientos_disponibles", "comodidades",
            "horarios_salida", "clases",
        ]


class DetalleRestauracionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleRestauracion
        fields = [
            "tipo_cocina", "es_vegano", "precio_medio", "requiere_reserva",
            "rango_precios", "abierto_ahora", "especialidades",
            "horario", "ubicacion_texto",
            "fecha_disponible_desde", "fecha_disponible_hasta",
            "fechas_no_disponibles", "turnos_disponibles", "turnos_ocupados",
        ]


class DetalleActividadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetalleActividad
        fields = [
            "duracion_estimada", "aforo_maximo", "horario_apertura", "guia_incluido",
            "dificultad", "duracion_texto", "ubicacion_texto",
            "incluye", "requisitos", "turnos_disponibles", "turnos_ocupados",
            "fecha_disponible_desde", "fecha_disponible_hasta",
            "fechas_no_disponibles",
        ]


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
            "valoracion", "num_resenas", "ciudad", "pais",
            "direccion", "moneda", "etiquetas", "destacado",
            "detalle_alojamiento", "detalle_transporte",
            "detalle_restauracion", "detalle_actividad",
        ]
