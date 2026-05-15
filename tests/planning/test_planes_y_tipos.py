import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from marketdata.models import CatalogoServicio, TipoServicio
from planning.models import EstadoReserva, Reserva

User = get_user_model()


def _jwt(client, email, password="secret123"):
    client.post(
        reverse("auth-register"),
        {"email": email, "password": password, "name": "T"},
        format="json",
    )
    log = client.post(
        reverse("auth-login"),
        {"email": email, "password": password},
        format="json",
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {log.data['access']}")


class PlanesApiTests(APITestCase):
    def test_crud_plan_basico(self):
        _jwt(self.client, "plan@example.com")
        lista = self.client.get(reverse("auth-mis-planes"))
        self.assertEqual(lista.status_code, status.HTTP_200_OK)
        self.assertEqual(lista.data, [])

        cre = self.client.post(
            reverse("auth-mis-planes"),
            {
                "nombre_plan": "Verano",
                "fecha_inicio": "2026-07-01",
                "fecha_fin": "2026-07-15",
            },
            format="json",
        )
        self.assertEqual(cre.status_code, status.HTTP_201_CREATED, cre.data)
        pid = cre.data["id_plan"]

        det = self.client.get(reverse("auth-plan-detail", kwargs={"pk": pid}))
        self.assertEqual(det.status_code, status.HTTP_200_OK)
        self.assertEqual(det.data["nombre_plan"], "Verano")

        dl = self.client.delete(reverse("auth-plan-detail", kwargs={"pk": pid}))
        self.assertEqual(dl.status_code, status.HTTP_204_NO_CONTENT)

    def test_item_no_puede_enlazar_reserva_de_otro_usuario(self):
        tipo = TipoServicio.objects.create(nombre_tipo="Actividad", icono="a")
        servicio = CatalogoServicio.objects.create(
            id_servicio="svc-item-sec",
            tipo=tipo,
            nombre="Tour",
            disponible=True,
        )
        victima = User.objects.create_user(
            username="vic@example.com",
            email="vic@example.com",
            password="secret123",
        )
        reserva_ajena = Reserva.objects.create(
            usuario=victima,
            servicio=servicio,
            fecha_inicio=datetime.date(2026, 9, 1),
            estado=EstadoReserva.CONFIRMADA,
        )

        _jwt(self.client, "atacante@example.com")
        pid = self.client.post(
            reverse("auth-mis-planes"),
            {
                "nombre_plan": "Robo",
                "fecha_inicio": "2026-09-01",
                "fecha_fin": "2026-09-02",
            },
            format="json",
        ).data["id_plan"]

        r = self.client.post(
            reverse("auth-plan-items", kwargs={"pk": pid}),
            {
                "nombre_servicio": "Item",
                "tipo": tipo.pk,
                "reserva": reserva_ajena.pk,
            },
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("reserva", r.data)


class TiposServicioApiTests(APITestCase):
    def test_tipos_requiere_auth(self):
        code = self.client.get(reverse("tipos-servicio")).status_code
        self.assertIn(code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_tipos_lista_autenticado(self):
        TipoServicio.objects.create(nombre_tipo="Actividad", icono="a")
        _jwt(self.client, "tipos@example.com")
        r = self.client.get(reverse("tipos-servicio"))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertTrue(len(r.data) >= 1)
