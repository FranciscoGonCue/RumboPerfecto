from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny

from .models import CatalogoServicio
from .serializers import CatalogoServicioSerializer

_SERVICIO_QUERYSET = (
    CatalogoServicio.objects
    .select_related(
        "tipo",
        "detalle_alojamiento",
        "detalle_transporte",
        "detalle_restauracion",
        "detalle_actividad",
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
        return _SERVICIO_QUERYSET.order_by("id_servicio")[:200]


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
        return _SERVICIO_QUERYSET
