from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import CatalogoServicio, ResenaServicio
from .serializers import CatalogoServicioSerializer, ResenaServicioSerializer


def catalogo_servicios_queryset():
    """
    Catálogo con tipos, detalles y relación resenas (lista en JSON al serializar).
    """
    return (
        CatalogoServicio.objects
        .select_related(
            "tipo",
            "detalle_alojamiento",
            "detalle_transporte",
            "detalle_restauracion",
            "detalle_actividad",
        )
        .prefetch_related(
            Prefetch(
                "resenas",
                queryset=ResenaServicio.objects.select_related("usuario").order_by("-creado_en"),
            ),
        )
    )


class CatalogoServicioListView(ListAPIView):
    """
    GET /api/servicios/
    Devuelve hasta 200 servicios del catálogo con sus detalles anidados.
    Endpoint público — no requiere autenticación.
    """
    serializer_class = CatalogoServicioSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        return catalogo_servicios_queryset().order_by("id_servicio")[:200]


class CatalogoServicioDetailView(RetrieveAPIView):
    """
    GET /api/servicios/<id>/
    Devuelve el detalle de un único servicio.
    Endpoint público — no requiere autenticación.
    """
    serializer_class = CatalogoServicioSerializer
    permission_classes = [AllowAny]
    lookup_field = "id_servicio"

    def get_queryset(self):
        return catalogo_servicios_queryset()


class ResenaServicioListCreateView(ListCreateAPIView):
    """
    GET /api/servicios/<id_servicio>/resenas/ — lista pública de reseñas.
    POST — crea reseña autenticado (una por usuario y servicio).
    """

    serializer_class = ResenaServicioSerializer
    pagination_class = None

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        sid = self.kwargs["id_servicio"]
        return (
            ResenaServicio.objects.select_related("usuario")
            .filter(servicio_id=sid)
            .order_by("-creado_en")
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["servicio"] = get_object_or_404(CatalogoServicio, pk=self.kwargs["id_servicio"])
        return ctx
