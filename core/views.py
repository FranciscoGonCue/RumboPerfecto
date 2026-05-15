from django.contrib.auth import authenticate
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
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

from core.geocoding import GeocodeLookupError, GeocodeNotFoundError, nominatim_geocode_first

from .serializers import (
    ChangePasswordSerializer,
    RegisterSerializer,
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
        except TokenError:
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
        servicios = catalogo_servicios_queryset().filter(usuario=request.user).order_by("id_servicio")
        return Response(CatalogoServicioSerializer(servicios, many=True).data)


class ServicioUpdateView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    CATALOGO_FIELDS = {
        "nombre",
        "descripcion",
        "precio_base",
        "imagen_url",
        "disponible",
        "ciudad",
        "pais",
        "direccion",
        "moneda",
        "etiquetas",
        "destacado",
        "ubicacion_lat",
        "ubicacion_lon",
    }
    ALOJAMIENTO_FIELDS = {
        "estrellas",
        "hora_checkin",
        "hora_checkout",
        "amenidades",
        "fecha_disponible_desde",
        "fecha_disponible_hasta",
        "fechas_no_disponibles",
    }
    ACTIVIDAD_FIELDS = {
        "duracion_estimada",
        "aforo_maximo",
        "horario_apertura",
        "guia_incluido",
        "dificultad",
        "duracion_texto",
        "ubicacion_texto",
        "incluye",
        "requisitos",
        "turnos_disponibles",
        "fecha_disponible_desde",
        "fecha_disponible_hasta",
        "fechas_no_disponibles",
    }
    RESTAURACION_FIELDS = {
        "tipo_cocina",
        "es_vegano",
        "precio_medio",
        "requiere_reserva",
        "rango_precios",
        "abierto_ahora",
        "especialidades",
        "horario",
        "ubicacion_texto",
        "fecha_disponible_desde",
        "fecha_disponible_hasta",
        "fechas_no_disponibles",
        "turnos_disponibles",
    }
    TRANSPORTE_FIELDS = {
        "ciudad_origen",
        "ciudad_destino",
        "compania",
        "codigo_vuelo",
        "duracion_minutos",
        "asientos_disponibles",
        "comodidades",
        "horarios_salida",
        "clases",
    }

    @staticmethod
    def _catalog_address_query(servicio):
        parts = [
            (servicio.direccion or "").strip(),
            (servicio.ciudad or "").strip(),
            (servicio.pais or "").strip(),
        ]
        return ", ".join(p for p in parts if p)

    @staticmethod
    def _user_sent_explicit_coords(data):
        if "ubicacion_lat" not in data or "ubicacion_lon" not in data:
            return False
        lat, lon = data.get("ubicacion_lat"), data.get("ubicacion_lon")
        if lat is None or lon is None:
            return False
        try:
            float(lat)
            float(lon)
            return True
        except (TypeError, ValueError):
            return False

    def _maybe_geocode_servicio(self, servicio, request_data, catalogo_data):
        query = self._catalog_address_query(servicio)
        if len(query.strip()) < 8:
            return

        address_changed = bool(set(catalogo_data) & {"direccion", "ciudad", "pais"})
        coords_missing = servicio.ubicacion_lat is None or servicio.ubicacion_lon is None

        if self._user_sent_explicit_coords(request_data):
            return

        if not coords_missing and not address_changed:
            return

        try:
            lat, lon, _display = nominatim_geocode_first(query)
        except (GeocodeLookupError, GeocodeNotFoundError):
            return

        servicio.ubicacion_lat = lat
        servicio.ubicacion_lon = lon
        servicio.save(update_fields=["ubicacion_lat", "ubicacion_lon"])

    def patch(self, request, id_servicio):
        try:
            servicio = CatalogoServicio.objects.select_related(
                "detalle_alojamiento",
                "detalle_actividad",
                "detalle_restauracion",
                "detalle_transporte",
            ).get(id_servicio=id_servicio, usuario=request.user)
        except CatalogoServicio.DoesNotExist:
            return Response({"detail": "No encontrado."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data

        catalogo_data = {k: v for k, v in data.items() if k in self.CATALOGO_FIELDS}
        if catalogo_data:
            for field, value in catalogo_data.items():
                setattr(servicio, field, value)
            servicio.save(update_fields=list(catalogo_data.keys()))

        self._update_detail(servicio, data)

        self._maybe_geocode_servicio(servicio, data, catalogo_data)

        servicio.refresh_from_db()
        serializer = CatalogoServicioSerializer(catalogo_servicios_queryset().get(pk=id_servicio))
        return Response(serializer.data)

    def _update_detail(self, servicio, data):
        detail_data = {k: v for k, v in data.items() if k in self.ALOJAMIENTO_FIELDS}
        if detail_data:
            obj, _ = DetalleAlojamiento.objects.get_or_create(servicio=servicio)
            for field, value in detail_data.items():
                setattr(obj, field, value)
            obj.save(update_fields=list(detail_data.keys()))

        detail_data = {k: v for k, v in data.items() if k in self.ACTIVIDAD_FIELDS}
        if detail_data:
            obj, _ = DetalleActividad.objects.get_or_create(servicio=servicio)
            for field, value in detail_data.items():
                setattr(obj, field, value)
            obj.save(update_fields=list(detail_data.keys()))

        detail_data = {k: v for k, v in data.items() if k in self.RESTAURACION_FIELDS}
        if detail_data:
            obj, _ = DetalleRestauracion.objects.get_or_create(servicio=servicio)
            for field, value in detail_data.items():
                setattr(obj, field, value)
            obj.save(update_fields=list(detail_data.keys()))

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
