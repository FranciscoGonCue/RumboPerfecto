from rest_framework import serializers

from marketdata.models import TipoServicio
from .models import EstadoPago, EstadoPlan, ItemPlan, PlanViaje, Reserva


class TipoServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoServicio
        fields = ['id_tipo', 'nombre_tipo', 'icono']


class ItemPlanSerializer(serializers.ModelSerializer):
    tipo_nombre = serializers.SerializerMethodField()
    reserva_id = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = ItemPlan
        fields = [
            'id_item',
            'nombre_servicio',
            'tipo',
            'tipo_nombre',
            'reserva_id',
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

    def get_tipo_nombre(self, obj):
        t = getattr(obj, 'tipo', None)
        if t is None:
            return None
        return getattr(t, 'nombre_tipo', None)


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
    reserva = serializers.PrimaryKeyRelatedField(
        queryset=Reserva.objects.all(),
        required=False,
        allow_null=True,
    )

    class Meta:
        model = ItemPlan
        fields = [
            'nombre_servicio',
            'tipo',
            'reserva',
            'fecha_hora_inicio',
            'fecha_hora_fin',
            'precio_estimado',
            'monto_total',
            'estado_pago',
            'localizador_confirmacion',
            'ubicacion_lat',
            'ubicacion_lon',
        ]

    def validate_reserva(self, value):
        if value is None:
            return value
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError('No autenticado.')
        if value.usuario_id != user.pk:
            raise serializers.ValidationError('Reserva no válida.')
        conflict = ItemPlan.objects.filter(reserva=value)
        if getattr(self, 'instance', None) is not None:
            conflict = conflict.exclude(pk=self.instance.pk)
        if conflict.exists():
            raise serializers.ValidationError('Esta reserva ya está añadida a un plan.')
        return value


class PlanViajeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanViaje
        fields = [
            'nombre_plan',
            'fecha_inicio',
            'fecha_fin',
            'estado_plan',
        ]


class ReservaSerializer(serializers.ModelSerializer):
    servicio_nombre = serializers.CharField(source='servicio.nombre', read_only=True)
    servicio_imagen = serializers.CharField(source='servicio.imagen_url', read_only=True)
    servicio_ciudad  = serializers.CharField(source='servicio.ciudad', read_only=True)
    servicio_tipo   = serializers.CharField(source='servicio.tipo.nombre_tipo', read_only=True, default=None)
    servicio_tipo_id = serializers.IntegerField(source='servicio.tipo_id', read_only=True, allow_null=True)
    usuario_email   = serializers.EmailField(source='usuario.email', read_only=True)
    usuario_nombre  = serializers.CharField(source='usuario.name', read_only=True, default=None)

    class Meta:
        model = Reserva
        fields = [
            'id', 'servicio', 'servicio_nombre', 'servicio_imagen',
            'servicio_ciudad', 'servicio_tipo', 'servicio_tipo_id',
            'usuario_email', 'usuario_nombre',
            'fecha_inicio', 'fecha_fin', 'turno', 'personas',
            'precio_total', 'estado', 'notas', 'creado_en',
        ]
        read_only_fields = ['id', 'creado_en']


class ReservaWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = [
            'servicio', 'fecha_inicio', 'fecha_fin',
            'turno', 'personas', 'precio_total', 'notas',
        ]
