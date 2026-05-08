from django.contrib.auth import authenticate
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from marketdata.models import (
    CatalogoServicio,
    DetalleAlojamiento,
    DetalleActividad,
    DetalleRestauracion,
    DetalleTransporte,
)
from marketdata.serializers import CatalogoServicioSerializer
from marketdata.views import catalogo_servicios_queryset
from .models import Activity, Trip
from .serializers import (
    ActivitySerializer,
    ActivityWriteSerializer,
    ChangePasswordSerializer,
    RegisterSerializer,
    TripSerializer,
    TripWriteSerializer,
    UpdateProfileSerializer,
    UserSerializer,
)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = (request.data.get("email") or "").strip().lower()
        password = request.data.get("password") or ""

        user = authenticate(request, username=email, password=password)
        if not user:
            return Response(
                {"detail": "Credenciales invalidas."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token requerido."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({"detail": "Refresh token invalido."}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = UpdateProfileSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data)


class MisServiciosView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        servicios = catalogo_servicios_queryset().filter(usuario=request.user).order_by('id_servicio')
        return Response(CatalogoServicioSerializer(servicios, many=True).data)


class ServicioUpdateView(APIView):
    """
    PATCH /api/auth/mis-servicios/<id_servicio>/
    Actualiza los campos del servicio y su detalle.
    Solo el propietario puede modificarlo.
    """
    permission_classes = [permissions.IsAuthenticated]

    # Campos permitidos por modelo
    CATALOGO_FIELDS = {
        'nombre', 'descripcion', 'precio_base', 'imagen_url', 'disponible',
        'ciudad', 'pais', 'direccion', 'moneda', 'valoracion', 'num_resenas',
        'etiquetas', 'destacado', 'ubicacion_lat', 'ubicacion_lon',
    }
    ALOJAMIENTO_FIELDS = {
        'estrellas', 'hora_checkin', 'hora_checkout', 'amenidades',
        'fecha_disponible_desde', 'fecha_disponible_hasta', 'fechas_no_disponibles',
    }
    ACTIVIDAD_FIELDS = {
        'duracion_estimada', 'aforo_maximo', 'horario_apertura', 'guia_incluido',
        'dificultad', 'duracion_texto', 'ubicacion_texto',
        'incluye', 'requisitos', 'turnos_disponibles',
        'fecha_disponible_desde', 'fecha_disponible_hasta', 'fechas_no_disponibles',
    }
    RESTAURACION_FIELDS = {
        'tipo_cocina', 'es_vegano', 'precio_medio', 'requiere_reserva',
        'rango_precios', 'abierto_ahora', 'especialidades', 'horario', 'ubicacion_texto',
        'fecha_disponible_desde', 'fecha_disponible_hasta', 'fechas_no_disponibles',
        'turnos_disponibles',
    }
    TRANSPORTE_FIELDS = {
        'ciudad_origen', 'ciudad_destino', 'compania', 'codigo_vuelo',
        'duracion_minutos', 'asientos_disponibles', 'comodidades',
        'horarios_salida', 'clases',
    }

    def patch(self, request, id_servicio):
        try:
            servicio = CatalogoServicio.objects.select_related(
                'detalle_alojamiento', 'detalle_actividad',
                'detalle_restauracion', 'detalle_transporte',
            ).get(id_servicio=id_servicio, usuario=request.user)
        except CatalogoServicio.DoesNotExist:
            return Response({'detail': 'No encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        data = request.data

        # ── CatalogoServicio ──────────────────────────────────────────────
        catalogo_data = {k: v for k, v in data.items() if k in self.CATALOGO_FIELDS}
        if catalogo_data:
            for field, value in catalogo_data.items():
                setattr(servicio, field, value)
            servicio.save(update_fields=list(catalogo_data.keys()))

        # ── Detalle específico ────────────────────────────────────────────
        self._update_detail(servicio, data)

        # Devolver el servicio actualizado completo
        servicio.refresh_from_db()
        serializer = CatalogoServicioSerializer(
            catalogo_servicios_queryset().get(pk=id_servicio)
        )
        return Response(serializer.data)

    def _update_detail(self, servicio, data):
        # Alojamiento
        detail_data = {k: v for k, v in data.items() if k in self.ALOJAMIENTO_FIELDS}
        if detail_data:
            obj, _ = DetalleAlojamiento.objects.get_or_create(servicio=servicio)
            for field, value in detail_data.items():
                setattr(obj, field, value)
            obj.save(update_fields=list(detail_data.keys()))

        # Actividad
        detail_data = {k: v for k, v in data.items() if k in self.ACTIVIDAD_FIELDS}
        if detail_data:
            obj, _ = DetalleActividad.objects.get_or_create(servicio=servicio)
            for field, value in detail_data.items():
                setattr(obj, field, value)
            obj.save(update_fields=list(detail_data.keys()))

        # Restauración
        detail_data = {k: v for k, v in data.items() if k in self.RESTAURACION_FIELDS}
        if detail_data:
            obj, _ = DetalleRestauracion.objects.get_or_create(servicio=servicio)
            for field, value in detail_data.items():
                setattr(obj, field, value)
            obj.save(update_fields=list(detail_data.keys()))

        # Transporte
        detail_data = {k: v for k, v in data.items() if k in self.TRANSPORTE_FIELDS}
        if detail_data:
            obj, _ = DetalleTransporte.objects.get_or_create(servicio=servicio)
            for field, value in detail_data.items():
                setattr(obj, field, value)
            obj.save(update_fields=list(detail_data.keys()))


class UpdateSellerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        seller = request.data.get("seller")
        if not isinstance(seller, bool):
            return Response({"detail": "El campo seller debe ser un booleano."}, status=status.HTTP_400_BAD_REQUEST)
        request.user.seller = seller
        request.user.save(update_fields=["seller"])
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Contraseña actualizada correctamente."})


class TripViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Trip.objects.filter(user=self.request.user)
            .prefetch_related("activities")
            .order_by("-start_date", "-created_at")
        )

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return TripWriteSerializer
        return TripSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ActivityViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Activity.objects.filter(trip__user=self.request.user).select_related("trip")
        trip_id = self.request.query_params.get("trip")
        if trip_id:
            queryset = queryset.filter(trip_id=trip_id)
        return queryset.order_by("day", "time", "created_at")

    def get_serializer_class(self):
        if self.action in {"create", "update", "partial_update"}:
            return ActivityWriteSerializer
        return ActivitySerializer

    def perform_create(self, serializer):
        trip_id = self.request.data.get("trip")
        trip = Trip.objects.filter(id=trip_id, user=self.request.user).first()
        if trip is None:
            raise PermissionDenied("No puedes agregar actividades a este viaje.")

        day = serializer.validated_data.get("day")
        if day is not None:
            trip_days = (trip.end_date - trip.start_date).days + 1
            if day < 1 or day > trip_days:
                raise ValidationError({"day": "El dia no puede ser mayor que la duracion del viaje."})

        serializer.save(trip=trip)

    def perform_update(self, serializer):
        activity = self.get_object()
        if activity.trip.user_id != self.request.user.id:
            raise PermissionDenied("No puedes modificar actividades de otro usuario.")

        day = serializer.validated_data.get("day", activity.day)
        trip_days = (activity.trip.end_date - activity.trip.start_date).days + 1
        if day < 1 or day > trip_days:
            raise ValidationError({"day": "El dia no puede ser mayor que la duracion del viaje."})

        serializer.save()

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def by_trip(self, request):
        trip_id = request.query_params.get("trip")
        if not trip_id:
            return Response({"detail": "El parametro trip es obligatorio."}, status=status.HTTP_400_BAD_REQUEST)
        items = self.get_queryset().filter(trip_id=trip_id)
        return Response(ActivitySerializer(items, many=True).data)
