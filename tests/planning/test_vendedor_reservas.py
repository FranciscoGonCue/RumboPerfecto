from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from marketdata.models import CatalogoServicio, TipoServicio
from planning.models import EstadoReserva, Reserva

User = get_user_model()


class VendedorReservaEstadoTests(APITestCase):
    def test_vendedor_confirma_reserva(self):
        self.client.post(
            reverse("auth-register"),
            {"email": "owner@v.com", "password": "pw12345", "name": "Owner"},
            format="json",
        )
        owner = User.objects.get(email__iexact="owner@v.com")
        tipo = TipoServicio.objects.create(nombre_tipo="Actividad", icono="x")
        servicio = CatalogoServicio.objects.create(
            id_servicio="vend-s1",
            tipo=tipo,
            nombre="Excursión",
            usuario=owner,
            disponible=True,
        )
        client_user = User.objects.create_user(
            username="buyer@v.com", email="buyer@v.com", password="buyer123"
        )
        reserva = Reserva.objects.create(
            usuario=client_user,
            servicio=servicio,
            fecha_inicio="2026-05-01",
            turno="09:00",
            personas=1,
            estado=EstadoReserva.PENDIENTE.value,
        )

        log = self.client.post(
            reverse("auth-login"),
            {"email": "owner@v.com", "password": "pw12345"},
            format="json",
        )
        self.assertEqual(log.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {log.data['access']}")

        url = reverse(
            "auth-servicio-reserva-estado",
            kwargs={"id_servicio": "vend-s1", "pk": reserva.pk},
        )
        r = self.client.patch(
            url, {"estado": EstadoReserva.CONFIRMADA.value}, format="json"
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.data)
        self.assertEqual(r.data["estado"], EstadoReserva.CONFIRMADA.value)
