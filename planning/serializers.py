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
            'ubicacion_direccion',
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
        queryset=Reserva.objects.none(),
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
            'ubicacion_direccion',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        user = getattr(request, "user", None)
        qs = (
            Reserva.objects.filter(usuario=user)
            if user is not None and user.is_authenticated
            else Reserva.objects.none()
        )
        self.fields["reserva"].queryset = qs

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

    def create(self, validated_data):
        self._ubicacion_desde_servicio_reserva(validated_data, instance=None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'reserva' in validated_data and validated_data['reserva'] is not None:
            self._ubicacion_desde_servicio_reserva(validated_data, instance=instance)
        return super().update(instance, validated_data)

    @staticmethod
    def _ubicacion_desde_servicio_reserva(validated_data, instance=None):
        reserva = validated_data.get('reserva')
        if reserva is None:
            return

        svc = reserva.servicio

        if instance is None:
            lat = validated_data.get('ubicacion_lat')
            lon = validated_data.get('ubicacion_lon')
            direccion = validated_data.get('ubicacion_direccion')
        else:
            lat = (
                validated_data['ubicacion_lat']
                if 'ubicacion_lat' in validated_data
                else instance.ubicacion_lat
            )
            lon = (
                validated_data['ubicacion_lon']
                if 'ubicacion_lon' in validated_data
                else instance.ubicacion_lon
            )
            direccion = (
                validated_data['ubicacion_direccion']
                if 'ubicacion_direccion' in validated_data
                else instance.ubicacion_direccion
            )

        if (lat is None or lon is None) and svc.ubicacion_lat is not None and svc.ubicacion_lon is not None:
            validated_data.setdefault('ubicacion_lat', svc.ubicacion_lat)
            validated_data.setdefault('ubicacion_lon', svc.ubicacion_lon)

        if not direccion:
            addr_parts = [
                getattr(svc, 'direccion', None),
                getattr(svc, 'ciudad', None),
                getattr(svc, 'pais', None),
            ]
            addr = ', '.join(str(p).strip() for p in addr_parts if p)
            if addr:
                validated_data.setdefault('ubicacion_direccion', addr)


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
    usuario_email = serializers.EmailField(source="usuario.email", read_only=True)
    usuario_nombre = serializers.SerializerMethodField()

    def get_usuario_nombre(self, obj):
        u = getattr(obj, "usuario", None)
        if u is None:
            return None
        fn = (u.get_full_name() or "").strip()
        if fn:
            return fn
        if getattr(u, "username", None):
            return u.username.strip()
        return (u.email or "").strip() or None

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
