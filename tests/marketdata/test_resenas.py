from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from marketdata.models import CatalogoServicio, ResenaServicio, TipoServicio

User = get_user_model()


def _register_and_token(client, email="rev@example.com"):
    client.post(
        reverse("auth-register"),
        {"email": email, "password": "secret123", "name": "Reviewer"},
        format="json",
    )
    login = client.post(
        reverse("auth-login"),
        {"email": email, "password": "secret123"},
        format="json",
    )
    return login.data["access"]


class ResenaServicioApiTests(APITestCase):
    def setUp(self):
        self.tipo = TipoServicio.objects.create(nombre_tipo="Actividad", icono="x")
        self.servicio = CatalogoServicio.objects.create(
            id_servicio="res-svc-1",
            tipo=self.tipo,
            nombre="Tour",
            disponible=True,
            valoracion=Decimal("4.0"),
            num_resenas=0,
        )

    def test_get_resenas_publico_sin_auth(self):
        url = reverse("servicios-resenas", kwargs={"id_servicio": "res-svc-1"})
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

    def test_post_resena_autenticado_y_actualiza_valoracion(self):
        token = _register_and_token(self.client)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("servicios-resenas", kwargs={"id_servicio": "res-svc-1"})
        r = self.client.post(
            url,
            {"mensaje": "Genial", "puntuacion": 5},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, r.data)
        self.servicio.refresh_from_db()
        self.assertEqual(self.servicio.num_resenas, 1)
        self.assertEqual(float(self.servicio.valoracion), 5.0)

    def test_segunda_resena_mismo_usuario_devuelve_400(self):
        token = _register_and_token(self.client, email="twice@example.com")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        url = reverse("servicios-resenas", kwargs={"id_servicio": "res-svc-1"})
        self.assertEqual(
            self.client.post(
                url, {"mensaje": "Primera", "puntuacion": 5}, format="json"
            ).status_code,
            status.HTTP_201_CREATED,
        )
        r2 = self.client.post(
            url, {"mensaje": "Duplicado", "puntuacion": 4}, format="json"
        )
        self.assertEqual(r2.status_code, status.HTTP_400_BAD_REQUEST)


class ResenaServicioModelTests(APITestCase):

    def test_save_sincroniza_valoracion(self):
        u = User.objects.create_user(username="m@example.com", email="m@example.com", password="x")
        tipo = TipoServicio.objects.create(nombre_tipo="A", icono="a")
        s = CatalogoServicio.objects.create(
            id_servicio="mod-sync",
            tipo=tipo,
            nombre="X",
            num_resenas=0,
            valoracion=None,
        )
        ResenaServicio.objects.create(usuario=u, servicio=s, mensaje="ok", puntuacion=4)
        s.refresh_from_db()
        self.assertEqual(s.num_resenas, 1)
        self.assertEqual(float(s.valoracion), 4.0)
