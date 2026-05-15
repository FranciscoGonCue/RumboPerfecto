from decimal import Decimal
import unittest.mock

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from marketdata.models import CatalogoServicio, TipoServicio

User = get_user_model()


def _auth_client(client, email="owner@example.com", password="secret123"):
    client.post(
        reverse("auth-register"),
        {"email": email, "password": password, "name": "Owner"},
        format="json",
    )
    login = client.post(
        reverse("auth-login"),
        {"email": email, "password": password},
        format="json",
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")


class ProfileAndSellerTests(APITestCase):
    def test_patch_me_actualiza_nombre(self):
        _auth_client(self.client, email="patch@example.com")
        me = self.client.patch(
            reverse("auth-me"),
            {"name": "Nuevo Nombre Apellido"},
            format="json",
        )
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertIn("Nuevo", me.data.get("first_name", ""))

    def test_seller_post_actualiza_flag(self):
        _auth_client(self.client, email="sell@example.com")
        r = self.client.post(reverse("auth-seller"), {"seller": True}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertTrue(r.data.get("seller"))

    def test_change_password(self):
        _auth_client(self.client, email="pwd@example.com", password="oldpass12")
        r = self.client.post(
            reverse("auth-change-password"),
            {"old_password": "oldpass12", "new_password": "newpass34"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        login_new = self.client.post(
            reverse("auth-login"),
            {"email": "pwd@example.com", "password": "newpass34"},
            format="json",
        )
        self.assertEqual(login_new.status_code, status.HTTP_200_OK)


class MisServiciosTests(APITestCase):
    def test_mis_servicios_lista_propios(self):
        email = "vend@test.com"
        _auth_client(self.client, email=email)
        user = User.objects.get(email__iexact=email)
        tipo = TipoServicio.objects.create(nombre_tipo="Hotel", icono="H")
        CatalogoServicio.objects.create(
            id_servicio="svc-owned",
            tipo=tipo,
            nombre="Mi hotel",
            usuario=user,
            disponible=True,
        )
        CatalogoServicio.objects.create(
            id_servicio="svc-otro",
            tipo=tipo,
            nombre="Otro",
            disponible=True,
            usuario=None,
        )
        r = self.client.get(reverse("auth-mis-servicios"))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        ids = {str(item["id_servicio"]) for item in r.data}
        self.assertIn("svc-owned", ids)
        self.assertNotIn("svc-otro", ids)


class ServicioPatchApiTests(APITestCase):
    def test_patch_actualiza_nombre_si_es_propietario(self):
        email = "patchsvc@example.com"
        _auth_client(self.client, email=email)
        user = User.objects.get(email__iexact=email)
        tipo = TipoServicio.objects.create(nombre_tipo="Hotel", icono="h")
        CatalogoServicio.objects.create(
            id_servicio="svc-patch",
            tipo=tipo,
            nombre="Antes",
            usuario=user,
            disponible=True,
        )
        r = self.client.patch(
            reverse("auth-mis-servicios-update", kwargs={"id_servicio": "svc-patch"}),
            {"nombre": "Después"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.data)
        self.assertEqual(r.data.get("nombre"), "Después")

    def test_patch_ignora_valoracion_y_num_resenas(self):
        email = "ratings-patch@example.com"
        _auth_client(self.client, email=email)
        user = User.objects.get(email__iexact=email)
        tipo = TipoServicio.objects.create(nombre_tipo="Hotel", icono="h")
        CatalogoServicio.objects.create(
            id_servicio="svc-rate-patch",
            tipo=tipo,
            nombre="Hotel",
            usuario=user,
            disponible=True,
            valoracion=Decimal("4.0"),
            num_resenas=3,
        )
        r = self.client.patch(
            reverse("auth-mis-servicios-update", kwargs={"id_servicio": "svc-rate-patch"}),
            {"valoracion": 5.0, "num_resenas": 999},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.data)
        self.assertEqual(float(r.data.get("valoracion")), 4.0)
        self.assertEqual(r.data.get("num_resenas"), 3)


class ServicioPatchGeocodeTests(APITestCase):
    @unittest.mock.patch("core.views.nominatim_geocode_first")
    def test_patch_rellena_coords_desde_direccion(self, mock_geo):
        mock_geo.return_value = (41.3874, 2.1686, "Barcelona")
        email = "geo-svc@example.com"
        _auth_client(self.client, email=email)
        user = User.objects.get(email__iexact=email)
        tipo = TipoServicio.objects.create(nombre_tipo="Hotel", icono="h")
        CatalogoServicio.objects.create(
            id_servicio="svc-geo-fill",
            tipo=tipo,
            nombre="Hotel",
            usuario=user,
            disponible=True,
            ubicacion_lat=None,
            ubicacion_lon=None,
            direccion="",
            ciudad="",
            pais="",
        )
        r = self.client.patch(
            reverse("auth-mis-servicios-update", kwargs={"id_servicio": "svc-geo-fill"}),
            {
                "direccion": "Plaça Catalunya 1",
                "ciudad": "Barcelona",
                "pais": "España",
            },
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.data)
        mock_geo.assert_called_once()
        self.assertAlmostEqual(float(r.data["ubicacion_lat"]), 41.3874, places=4)
        self.assertAlmostEqual(float(r.data["ubicacion_lon"]), 2.1686, places=4)

    @unittest.mock.patch("core.views.nominatim_geocode_first")
    def test_patch_coord_explicitas_no_llama_nominatim(self, mock_geo):
        mock_geo.return_value = (99.0, 99.0, "X")
        email = "geo-manual@example.com"
        _auth_client(self.client, email=email)
        user = User.objects.get(email__iexact=email)
        tipo = TipoServicio.objects.create(nombre_tipo="Hotel", icono="h")
        CatalogoServicio.objects.create(
            id_servicio="svc-geo-manual",
            tipo=tipo,
            nombre="Hotel",
            usuario=user,
            disponible=True,
            direccion="Calle X",
            ciudad="Madrid",
            pais="España",
            ubicacion_lat=None,
            ubicacion_lon=None,
        )
        r = self.client.patch(
            reverse("auth-mis-servicios-update", kwargs={"id_servicio": "svc-geo-manual"}),
            {"ubicacion_lat": 40.4168, "ubicacion_lon": -3.7038},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.data)
        mock_geo.assert_not_called()
        self.assertAlmostEqual(float(r.data["ubicacion_lat"]), 40.4168, places=4)
        self.assertAlmostEqual(float(r.data["ubicacion_lon"]), -3.7038, places=4)

    @unittest.mock.patch("core.views.nominatim_geocode_first")
    def test_patch_geocode_fallo_conserva_coords_previas(self, mock_geo):
        from core.geocoding import GeocodeNotFoundError

        mock_geo.side_effect = GeocodeNotFoundError()

        email = "geo-fail@example.com"
        _auth_client(self.client, email=email)
        user = User.objects.get(email__iexact=email)
        tipo = TipoServicio.objects.create(nombre_tipo="Hotel", icono="h")
        CatalogoServicio.objects.create(
            id_servicio="svc-geo-fail",
            tipo=tipo,
            nombre="Hotel",
            usuario=user,
            disponible=True,
            direccion="Old",
            ciudad="Valencia",
            pais="España",
            ubicacion_lat=39.47,
            ubicacion_lon=-0.376,
        )
        r = self.client.patch(
            reverse("auth-mis-servicios-update", kwargs={"id_servicio": "svc-geo-fail"}),
            {"direccion": "Calle inventada xyzqwerty 999"},
            format="json",
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK, r.data)
        self.assertAlmostEqual(float(r.data["ubicacion_lat"]), 39.47, places=3)
        self.assertAlmostEqual(float(r.data["ubicacion_lon"]), -0.376, places=3)
