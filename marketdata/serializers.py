from django.contrib.auth import get_user_model
from django.db import IntegrityError

from rest_framework import serializers
from .models import (
    TipoServicio, CatalogoServicio, ResenaServicio,
    DetalleAlojamiento, DetalleTransporte,
    DetalleRestauracion, DetalleActividad,
)

User = get_user_model()


class ResenaUsuarioSerializer(serializers.ModelSerializer):

    nombre = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "nombre"]

    def get_nombre(self, obj):
        fn = obj.get_full_name().strip()
        return fn if fn else obj.username


class ResenaServicioSerializer(serializers.ModelSerializer):
    usuario = ResenaUsuarioSerializer(read_only=True)
    id_servicio = serializers.CharField(source="servicio_id", read_only=True)

    class Meta:
        model = ResenaServicio
        fields = ["id", "usuario", "mensaje", "puntuacion", "id_servicio", "creado_en"]
        read_only_fields = ["id", "usuario", "id_servicio", "creado_en"]

    def create(self, validated_data):
        validated_data["usuario"] = self.context["request"].user
        validated_data["servicio"] = self.context["servicio"]
        try:
            return super().create(validated_data)
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {"non_field_errors": ["Ya existe una reseña tuya para este servicio."]}
            ) from exc


class ResenaServicioAnidadaSerializer(serializers.ModelSerializer):

    usuario = ResenaUsuarioSerializer(read_only=True)

    class Meta:
        model = ResenaServicio
        fields = ["id", "usuario", "mensaje", "puntuacion", "creado_en"]


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
    resenas = ResenaServicioAnidadaSerializer(many=True, read_only=True)

    class Meta:
        model = CatalogoServicio
        fields = [
            "id_servicio", "tipo", "nombre", "descripcion",
            "precio_base", "ubicacion_lat", "ubicacion_lon",
            "imagen_url", "disponible",
            "valoracion", "num_resenas", "ciudad", "pais",
            "direccion", "moneda", "etiquetas", "destacado",
            "resenas",
            "detalle_alojamiento", "detalle_transporte",
            "detalle_restauracion", "detalle_actividad",
        ]
