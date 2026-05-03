from rest_framework import serializers

from marketdata.models import TipoServicio
from .models import EstadoPago, EstadoPlan, ItemPlan, PlanViaje


class TipoServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoServicio
        fields = ['id_tipo', 'nombre_tipo', 'icono']


class ItemPlanSerializer(serializers.ModelSerializer):
    tipo_nombre = serializers.CharField(source='tipo.nombre', read_only=True, default=None)

    class Meta:
        model = ItemPlan
        fields = [
            'id_item',
            'nombre_servicio',
            'tipo',
            'tipo_nombre',
            'fecha_hora_inicio',
            'fecha_hora_fin',
            'precio_estimado',
            'monto_total',
            'estado_pago',
            'localizador_confirmacion',
            'fecha_transaccion',
            'ubicacion_lat',
            'ubicacion_lon',
        ]


class PlanViajeSerializer(serializers.ModelSerializer):
    items = ItemPlanSerializer(many=True, read_only=True)

    class Meta:
        model = PlanViaje
        fields = [
            'id_plan',
            'nombre_plan',
            'fecha_inicio',
            'fecha_fin',
            'estado_plan',
            'items',
        ]


class ItemPlanWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPlan
        fields = [
            'nombre_servicio',
            'tipo',
            'fecha_hora_inicio',
            'fecha_hora_fin',
            'precio_estimado',
            'monto_total',
            'estado_pago',
            'localizador_confirmacion',
            'ubicacion_lat',
            'ubicacion_lon',
        ]


class PlanViajeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanViaje
        fields = [
            'nombre_plan',
            'fecha_inicio',
            'fecha_fin',
            'estado_plan',
        ]
