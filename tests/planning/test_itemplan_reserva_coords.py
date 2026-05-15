import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from marketdata.models import CatalogoServicio, TipoServicio
from planning.models import EstadoReserva, PlanViaje, Reserva

User = get_user_model()


class ItemPlanDesdeReservaCoordsTests(APITestCase):
    def test_post_item_con_reserva_copia_coords_servicio(self):
        self.client.post(
            reverse("auth-register"),
            {"email": "coords-plan@example.com", "password": "secret123", "name": "U"},
            format="json",
        )
        login = self.client.post(
            reverse("auth-login"),
            {"email": "coords-plan@example.com", "password": "secret123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")
        user = User.objects.get(email__iexact="coords-plan@example.com")

        tipo = TipoServicio.objects.create(nombre_tipo="Hotel", icono="H")
        svc = CatalogoServicio.objects.create(
            id_servicio="srv-map-coords",
            tipo=tipo,
            nombre="Hotel Map",
            disponible=True,
            ubicacion_lat=41.387,
            ubicacion_lon=2.168,
            direccion="Plaza Catalunya 1",
            ciudad="Barcelona",
            pais="España",
        )
        plan = PlanViaje.objects.create(
            usuario=user,
            nombre_plan="Viaje",
            fecha_inicio=datetime.date(2026, 8, 1),
            fecha_fin=datetime.date(2026, 8, 10),
        )
        reserva = Reserva.objects.create(
            usuario=user,
            servicio=svc,
            fecha_inicio=datetime.date(2026, 8, 3),
            personas=2,
            estado=EstadoReserva.PENDIENTE,
        )

        r = self.client.post(
            reverse("auth-plan-items", kwargs={"pk": plan.pk}),
            {
                "nombre_servicio": "Noche hotel",
                "tipo": tipo.id_tipo,
                "reserva": reserva.pk,
                "fecha_hora_inicio": "2026-08-03T14:00:00",
                "precio_estimado": 100,
            },
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, r.data)
        self.assertAlmostEqual(float(r.data["ubicacion_lat"]), 41.387, places=5)
        self.assertAlmostEqual(float(r.data["ubicacion_lon"]), 2.168, places=5)
        self.assertIn("Barcelona", r.data["ubicacion_direccion"])
