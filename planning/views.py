from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

import datetime
from typing import Optional

from marketdata.models import (
    CatalogoServicio, TipoServicio,
    DetalleAlojamiento, DetalleActividad, DetalleRestauracion,
)
from .models import EstadoReserva, ItemPlan, PlanViaje, Reserva
from .serializers import (
    ItemPlanSerializer, ItemPlanWriteSerializer,
    PlanViajeSerializer, PlanViajeWriteSerializer,
    ReservaSerializer, ReservaWriteSerializer,
    TipoServicioSerializer,
)


def _turnos_equivalentes(a: str, b: str) -> bool:
    x = (a or '').strip()
    y = (b or '').strip()
    if not x or not y:
        return False
    if x == y:
        return True
    hx = x[:5] if len(x) >= 5 else x
    hy = y[:5] if len(y) >= 5 else y
    return hx == hy


def _canon_turno(slots: list, turno_reserva: str) -> str:
    tr = (turno_reserva or '').strip()
    for slot in slots:
        if _turnos_equivalentes(slot, tr):
            return slot
    return tr


def _turno_en_lista(turno: str, ocupados: list) -> bool:
    return any(_turnos_equivalentes(turno, o) for o in ocupados)


def _turnos_restantes_dia(slots: list, fecha_key: str, ocupados_por_fecha: dict) -> list:
    bloq = ocupados_por_fecha.get(fecha_key) or []
    return [t for t in slots if not _turno_en_lista(t, bloq)]


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
        serializer = ItemPlanWriteSerializer(data=request.data, context={'request': request})
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
        serializer = ItemPlanWriteSerializer(item, data=request.data, partial=True, context={'request': request})
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


class MisReservasView(APIView):
    """
    GET  /api/auth/mis-reservas/ — Reservas del usuario autenticado.
    POST /api/auth/mis-reservas/ — Crear una nueva reserva.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reservas = (
            Reserva.objects
            .filter(usuario=request.user)
            .select_related('servicio', 'servicio__tipo')
            .order_by('-creado_en')
        )
        return Response(ReservaSerializer(reservas, many=True).data)

    def post(self, request):
        serializer = ReservaWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        conflict = MisReservasView._conflicto_turno(serializer.validated_data)
        if conflict:
            return Response({'detail': conflict}, status=status.HTTP_409_CONFLICT)

        reserva = serializer.save(usuario=request.user)
        self._bloquear_fechas(reserva)
        return Response(ReservaSerializer(reserva).data, status=status.HTTP_201_CREATED)

    @staticmethod
    def _conflicto_turno(data: dict) -> Optional[str]:
        """Evita doble reserva del mismo turno el mismo día (actividad / restauración)."""
        servicio = data.get('servicio')
        if servicio is None:
            return None
        fecha_inicio = data.get('fecha_inicio')
        turno = (data.get('turno') or '').strip()
        if not fecha_inicio or not turno:
            return None
        fecha_key = str(fecha_inicio)
        for detalle in _iter_actividad_rest_detalle(servicio):
            slots = list(detalle.turnos_disponibles or [])
            if not slots:
                fechas_nd = detalle.fechas_no_disponibles or []
                if fecha_key in fechas_nd:
                    return 'Esa fecha ya no está disponible.'
                continue
            ocupados = dict(detalle.turnos_ocupados or {})
            bloq = list(ocupados.get(fecha_key) or [])
            canon = _canon_turno(slots, turno)
            if _turno_en_lista(canon, bloq):
                return 'Ese turno ya no está disponible para la fecha elegida.'
        return None

    @staticmethod
    def _bloquear_fechas(reserva: 'Reserva'):
        """Alojamiento: bloquea el rango en fechas_no_disponibles.
        Actividad / restaurante: marca turno como ocupado; el día solo va a fechas_no_disponibles
        cuando no queden turnos libres.
        """
        servicio = reserva.servicio

        fechas_nuevas: list[str] = []
        fecha = reserva.fecha_inicio
        fin = reserva.fecha_fin or reserva.fecha_inicio
        while fecha <= fin:
            fechas_nuevas.append(str(fecha))
            fecha += datetime.timedelta(days=1)

        def _update_alojamiento(obj):
            actual = obj.fechas_no_disponibles or []
            nueva_lista = sorted(set(actual) | set(fechas_nuevas))
            obj.fechas_no_disponibles = nueva_lista
            obj.save(update_fields=['fechas_no_disponibles'])

        try:
            _update_alojamiento(servicio.detalle_alojamiento)
            return
        except DetalleAlojamiento.DoesNotExist:
            pass

        try:
            det = servicio.detalle_actividad
            MisReservasView._ocupar_turno_actividad_restauracion(det, reserva)
            return
        except DetalleActividad.DoesNotExist:
            pass
        try:
            det = servicio.detalle_restauracion
            MisReservasView._ocupar_turno_actividad_restauracion(det, reserva)
        except DetalleRestauracion.DoesNotExist:
            pass

    @staticmethod
    def _ocupar_turno_actividad_restauracion(detalle, reserva: 'Reserva'):
        fecha_key = str(reserva.fecha_inicio)
        turno_raw = (reserva.turno or '').strip()
        slots = list(detalle.turnos_disponibles or [])
        ocupados = dict(detalle.turnos_ocupados or {})

        fechas_nd = set(detalle.fechas_no_disponibles or [])
        update_fields: list[str] = ['turnos_ocupados']

        if not slots:
            # Sin plantilla de turnos: el día completo queda indisponible
            fechas_nd.add(fecha_key)
            detalle.fechas_no_disponibles = sorted(fechas_nd)
            detalle.save(update_fields=['fechas_no_disponibles'])
            return

        if not turno_raw:
            return

        canon = _canon_turno(slots, turno_raw)
        lista_dia = list(ocupados.get(fecha_key) or [])
        if not _turno_en_lista(canon, lista_dia):
            lista_dia.append(canon)
        ocupados[fecha_key] = lista_dia
        detalle.turnos_ocupados = ocupados

        restantes = _turnos_restantes_dia(slots, fecha_key, ocupados)
        if not restantes:
            fechas_nd.add(fecha_key)
            detalle.fechas_no_disponibles = sorted(fechas_nd)
            update_fields.append('fechas_no_disponibles')

        detalle.save(update_fields=update_fields)


def _iter_actividad_rest_detalle(servicio):
    try:
        yield servicio.detalle_actividad
    except DetalleActividad.DoesNotExist:
        pass
    try:
        yield servicio.detalle_restauracion
    except DetalleRestauracion.DoesNotExist:
        pass


class ReservaDetailView(APIView):
    """
    GET    /api/auth/mis-reservas/<id>/ — Detalle de una reserva del usuario.
    PATCH  /api/auth/mis-reservas/<id>/ — Actualizar estado (ej. cancelar).
    DELETE /api/auth/mis-reservas/<id>/ — Eliminar reserva.
    """
    permission_classes = [permissions.IsAuthenticated]

    def _get_reserva(self, request, pk):
        return get_object_or_404(Reserva, pk=pk, usuario=request.user)

    def get(self, request, pk):
        return Response(ReservaSerializer(self._get_reserva(request, pk)).data)

    def patch(self, request, pk):
        reserva = self._get_reserva(request, pk)
        allowed = {'estado', 'notas'}
        data = {k: v for k, v in request.data.items() if k in allowed}
        for field, value in data.items():
            setattr(reserva, field, value)
        reserva.save(update_fields=list(data.keys()))
        return Response(ReservaSerializer(reserva).data)

    def delete(self, request, pk):
        self._get_reserva(request, pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ServicioReservasView(APIView):
    """
    GET /api/auth/mis-servicios/<id_servicio>/reservas/
    Lista las reservas de un servicio que pertenece al usuario autenticado (vendedor).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, id_servicio):
        servicio = get_object_or_404(
            CatalogoServicio, id_servicio=id_servicio, usuario=request.user
        )
        reservas = (
            Reserva.objects
            .filter(servicio=servicio)
            .select_related('usuario', 'servicio', 'servicio__tipo')
            .order_by('-creado_en')
        )
        return Response(ReservaSerializer(reservas, many=True).data)


class ServicioReservaEstadoView(APIView):
    """
    PATCH /api/auth/mis-servicios/<id_servicio>/reservas/<pk>/
    El propietario del servicio confirma o cancela una reserva de ese servicio.
    """
    permission_classes = [permissions.IsAuthenticated]
    _ESTADOS_VENDEDOR = frozenset({
        EstadoReserva.CONFIRMADA.value,
        EstadoReserva.CANCELADA.value,
    })

    def patch(self, request, id_servicio, pk):
        servicio = get_object_or_404(
            CatalogoServicio, id_servicio=id_servicio, usuario=request.user
        )
        reserva = get_object_or_404(Reserva, pk=pk, servicio=servicio)
        estado = request.data.get('estado')
        if estado not in self._ESTADOS_VENDEDOR:
            return Response(
                {'detail': 'Solo se admite estado Confirmada o Cancelada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reserva.estado = estado
        reserva.save(update_fields=['estado'])
        reserva = (
            Reserva.objects
            .select_related('usuario', 'servicio', 'servicio__tipo')
            .get(pk=reserva.pk)
        )
        return Response(ReservaSerializer(reserva).data)
