from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny

from .models import CatalogoServicio
from .serializers import CatalogoServicioSerializer


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
        return (
            CatalogoServicio.objects
            .select_related(
                "tipo",
                "detalle_alojamiento",
                "detalle_transporte",
                "detalle_restauracion",
                "detalle_actividad",
            )
            .order_by("id_servicio")[:200]
        )
