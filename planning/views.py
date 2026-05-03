from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from marketdata.models import TipoServicio
from .models import ItemPlan, PlanViaje
from .serializers import (
    ItemPlanSerializer, ItemPlanWriteSerializer,
    PlanViajeSerializer, PlanViajeWriteSerializer,
    TipoServicioSerializer,
)


class MisPlansView(APIView):
    """
    GET  /api/auth/mis-planes/ — Lista todos los PlanViaje del usuario.
    POST /api/auth/mis-planes/ — Crea un nuevo PlanViaje para el usuario.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        planes = (
            PlanViaje.objects
            .filter(usuario=request.user)
            .prefetch_related('items__tipo')
            .order_by('-fecha_inicio', '-id_plan')
        )
        serializer = PlanViajeSerializer(planes, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PlanViajeWriteSerializer(data=request.data)
        if serializer.is_valid():
            plan = serializer.save(usuario=request.user)
            return Response(PlanViajeSerializer(plan).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlanDetailView(APIView):
    """
    GET    /api/auth/mis-planes/<id>/ — Detalle completo de un PlanViaje del usuario.
    DELETE /api/auth/mis-planes/<id>/ — Elimina un PlanViaje del usuario.
    """
    permission_classes = [permissions.IsAuthenticated]

    def _get_plan(self, request, pk):
        return get_object_or_404(PlanViaje, pk=pk, usuario=request.user)

    def get(self, request, pk):
        plan = self._get_plan(request, pk)
        plan = PlanViaje.objects.prefetch_related('items__tipo').get(pk=plan.pk)
        return Response(PlanViajeSerializer(plan).data)

    def delete(self, request, pk):
        plan = self._get_plan(request, pk)
        plan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PlanItemsView(APIView):
    """POST /api/auth/mis-planes/<id>/items/ — Añade un ItemPlan a un plan del usuario."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        plan = get_object_or_404(PlanViaje, pk=pk, usuario=request.user)
        serializer = ItemPlanWriteSerializer(data=request.data)
        if serializer.is_valid():
            item = serializer.save(plan=plan)
            return Response(ItemPlanSerializer(item).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlanItemDetailView(APIView):
    """PATCH/DELETE /api/auth/mis-planes/<pk>/items/<item_pk>/"""
    permission_classes = [permissions.IsAuthenticated]

    def _get_item(self, request, pk, item_pk):
        plan = get_object_or_404(PlanViaje, pk=pk, usuario=request.user)
        return get_object_or_404(ItemPlan, pk=item_pk, plan=plan)

    def patch(self, request, pk, item_pk):
        item = self._get_item(request, pk, item_pk)
        serializer = ItemPlanWriteSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(ItemPlanSerializer(item).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, item_pk):
        item = self._get_item(request, pk, item_pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TiposServicioView(APIView):
    """GET /api/tipos-servicio/ — Lista todos los tipos de servicio disponibles."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        tipos = TipoServicio.objects.all().order_by('nombre_tipo')
        return Response(TipoServicioSerializer(tipos, many=True).data)
