import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from marketdata.models import CatalogoServicio, DetalleActividad, TipoServicio
from planning.models import EstadoReserva, Reserva
from planning.serializers import ReservaSerializer

User = get_user_model()


class ReservaSerializerTests(APITestCase):
    def test_usuario_nombre_usa_nombre_completo(self):
        user = User.objects.create_user(
            username="u1@test.com",
            email="u1@test.com",
            password="secret123",
            first_name="Ana",
            last_name="García",
        )
        tipo = TipoServicio.objects.create(nombre_tipo="Actividad", icono="x")
        servicio = CatalogoServicio.objects.create(
            id_servicio="ser-serial",
            tipo=tipo,
            nombre="Tour",
            disponible=True,
        )
        reserva = Reserva.objects.create(
            usuario=user,
            servicio=servicio,
            fecha_inicio=datetime.date(2026, 7, 1),
            turno="10:00",
            personas=1,
        )
        data = ReservaSerializer(reserva).data
        self.assertEqual(data["usuario_nombre"], "Ana García")
        self.assertEqual(data["usuario_email"], "u1@test.com")


class ReservaDisponibilidadTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="booker@test.com",
            email="booker@test.com",
            password="secret123",
        )
        self.tipo = TipoServicio.objects.create(nombre_tipo="Actividad", icono="x")
        self.servicio = CatalogoServicio.objects.create(
            id_servicio="act-lib-1",
            tipo=self.tipo,
            nombre="Kayak",
            disponible=True,
        )
        DetalleActividad.objects.create(
            servicio=self.servicio,
            turnos_disponibles=["09:00", "11:00"],
            turnos_ocupados={},
            fechas_no_disponibles=[],
        )

    def test_delete_reserva_libera_turno(self):
        self.client.force_authenticate(user=self.user)
        cre = self.client.post(
            reverse("auth-mis-reservas"),
            {
                "servicio": "act-lib-1",
                "fecha_inicio": "2026-06-15",
                "turno": "09:00",
                "personas": 1,
            },
            format="json",
        )
        self.assertEqual(cre.status_code, status.HTTP_201_CREATED, cre.data)
        rid = cre.data["id"]
        det = DetalleActividad.objects.get(servicio_id="act-lib-1")
        self.assertIn("09:00", (det.turnos_ocupados or {}).get("2026-06-15", []))

        dl = self.client.delete(reverse("auth-reserva-detail", kwargs={"pk": rid}))
        self.assertEqual(dl.status_code, status.HTTP_204_NO_CONTENT)
        det.refresh_from_db()
        self.assertFalse((det.turnos_ocupados or {}).get("2026-06-15"))

    def test_patch_cancelada_libera_turno(self):
        self.client.force_authenticate(user=self.user)
        cre = self.client.post(
            reverse("auth-mis-reservas"),
            {
                "servicio": "act-lib-1",
                "fecha_inicio": "2026-06-20",
                "turno": "11:00",
                "personas": 1,
            },
            format="json",
        )
        self.assertEqual(cre.status_code, status.HTTP_201_CREATED, cre.data)
        rid = cre.data["id"]
        patch = self.client.patch(
            reverse("auth-reserva-detail", kwargs={"pk": rid}),
            {"estado": EstadoReserva.CANCELADA.value},
            format="json",
        )
        self.assertEqual(patch.status_code, status.HTTP_200_OK, patch.data)
        det = DetalleActividad.objects.get(servicio_id="act-lib-1")
        self.assertFalse((det.turnos_ocupados or {}).get("2026-06-20"))
        self.assertEqual(
            Reserva.objects.get(pk=rid).estado, EstadoReserva.CANCELADA.value
        )


class ReservaTurnoConflictoTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="c1@test.com", email="c1@test.com", password="secret123"
        )
        self.tipo = TipoServicio.objects.create(nombre_tipo="Actividad", icono="x")
        self.servicio = CatalogoServicio.objects.create(
            id_servicio="act-conf",
            tipo=self.tipo,
            nombre="Surf",
            disponible=True,
        )
        DetalleActividad.objects.create(
            servicio=self.servicio,
            turnos_disponibles=["10:00"],
            turnos_ocupados={},
            fechas_no_disponibles=[],
        )

    def test_segunda_reserva_mismo_turno_409(self):
        self.client.force_authenticate(user=self.user)
        payload = {
            "servicio": "act-conf",
            "fecha_inicio": "2026-07-01",
            "turno": "10:00",
            "personas": 1,
        }
        first = self.client.post(reverse("auth-mis-reservas"), payload, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        second = self.client.post(reverse("auth-mis-reservas"), payload, format="json")
        self.assertEqual(second.status_code, status.HTTP_409_CONFLICT)


class AlojamientoReservaLiberacionTests(APITestCase):
    def setUp(self):
        from marketdata.models import DetalleAlojamiento

        self.user = User.objects.create_user(
            username="htl-user@test.com",
            email="htl-user@test.com",
            password="secret123",
        )
        self.tipo = TipoServicio.objects.create(nombre_tipo="Alojamiento", icono="b")
        self.servicio = CatalogoServicio.objects.create(
            id_servicio="htl-blq",
            tipo=self.tipo,
            nombre="Casa rural",
            disponible=True,
        )
        DetalleAlojamiento.objects.create(servicio=self.servicio, fechas_no_disponibles=[])

    def test_reserva_rango_libera_al_borrar(self):
        self.client.force_authenticate(user=self.user)
        cre = self.client.post(
            reverse("auth-mis-reservas"),
            {
                "servicio": "htl-blq",
                "fecha_inicio": "2026-09-10",
                "fecha_fin": "2026-09-11",
                "personas": 2,
            },
            format="json",
        )
        self.assertEqual(cre.status_code, status.HTTP_201_CREATED, cre.data)
        rid = cre.data["id"]

        self.servicio.refresh_from_db()
        det = self.servicio.detalle_alojamiento
        blocked = det.fechas_no_disponibles or []
        self.assertIn("2026-09-10", blocked)
        self.assertIn("2026-09-11", blocked)

        self.client.delete(reverse("auth-reserva-detail", kwargs={"pk": rid}))
        det.refresh_from_db()
        nuevas = det.fechas_no_disponibles or []
        self.assertNotIn("2026-09-10", nuevas)
        self.assertNotIn("2026-09-11", nuevas)
