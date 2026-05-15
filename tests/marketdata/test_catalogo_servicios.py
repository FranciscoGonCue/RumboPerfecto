from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from marketdata.models import CatalogoServicio, DetalleActividad, TipoServicio


def _make_tipo(**kwargs):
    defaults = {"nombre_tipo": "Actividad", "icono": "🏃"}
    defaults.update(kwargs)
    return TipoServicio.objects.create(**defaults)


def _make_servicio(id_servicio, tipo=None, **kwargs):
    defaults = {
        "nombre": "Servicio de prueba",
        "descripcion": "Descripción de prueba",
        "precio_base": 50.0,
        "ciudad": "Madrid",
        "pais": "España",
        "disponible": True,
        "valoracion": 4.5,
        "num_resenas": 10,
    }
    defaults.update(kwargs)
    return CatalogoServicio.objects.create(
        id_servicio=str(id_servicio), tipo=tipo, **defaults
    )


class ServicioDetailViewTests(APITestCase):

    def setUp(self):
        self.tipo = _make_tipo()
        self.servicio = _make_servicio("1", tipo=self.tipo, nombre="Senderismo en el Teide")

    def test_detalle_devuelve_200(self):
        url = reverse("servicios-detail", kwargs={"id_servicio": "1"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detalle_contiene_campos_esperados(self):
        url = reverse("servicios-detail", kwargs={"id_servicio": "1"})
        data = self.client.get(url).json()
        campos = [
            "id_servicio",
            "nombre",
            "descripcion",
            "precio_base",
            "ciudad",
            "pais",
            "valoracion",
            "num_resenas",
            "detalle_alojamiento",
            "detalle_transporte",
            "detalle_restauracion",
            "detalle_actividad",
        ]
        for campo in campos:
            self.assertIn(campo, data, msg=f"Falta campo '{campo}'")

    def test_detalle_devuelve_datos_correctos(self):
        data = self.client.get(
            reverse("servicios-detail", kwargs={"id_servicio": "1"})
        ).json()
        self.assertEqual(data["id_servicio"], "1")
        self.assertEqual(data["nombre"], "Senderismo en el Teide")
        self.assertEqual(float(data["precio_base"]), 50.0)

    def test_detalle_es_publico_sin_autenticacion(self):
        self.client.credentials()
        url = reverse("servicios-detail", kwargs={"id_servicio": "1"})
        self.assertEqual(self.client.get(url).status_code, status.HTTP_200_OK)

    def test_detalle_incluye_tipo_anidado(self):
        data = self.client.get(
            reverse("servicios-detail", kwargs={"id_servicio": "1"})
        ).json()
        self.assertIsNotNone(data["tipo"])
        self.assertEqual(data["tipo"]["nombre_tipo"], "Actividad")

    def test_detalle_incluye_detalle_actividad_anidado(self):
        DetalleActividad.objects.create(
            servicio=self.servicio,
            duracion_estimada=120,
            dificultad="Moderado",
            guia_incluido=True,
        )
        data = self.client.get(
            reverse("servicios-detail", kwargs={"id_servicio": "1"})
        ).json()
        self.assertIsNotNone(data["detalle_actividad"])
        self.assertEqual(data["detalle_actividad"]["duracion_estimada"], 120)

    def test_detalle_sin_detalle_actividad_devuelve_null(self):
        data = self.client.get(
            reverse("servicios-detail", kwargs={"id_servicio": "1"})
        ).json()
        self.assertIsNone(data["detalle_actividad"])

    def test_multiples_servicios_devuelven_el_correcto(self):
        _make_servicio("2", tipo=self.tipo, nombre="Kayak en las Cíes")
        _make_servicio("3", tipo=self.tipo, nombre="Ruta por Doñana")
        for id_s, nombre in [
            ("1", "Senderismo en el Teide"),
            ("2", "Kayak en las Cíes"),
            ("3", "Ruta por Doñana"),
        ]:
            data = self.client.get(
                reverse("servicios-detail", kwargs={"id_servicio": id_s})
            ).json()
            self.assertEqual(data["nombre"], nombre)

    def test_id_inexistente_devuelve_404(self):
        url = reverse("servicios-detail", kwargs={"id_servicio": "9999"})
        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_metodo_post_no_permitido(self):
        url = reverse("servicios-detail", kwargs={"id_servicio": "1"})
        r = self.client.post(url, {"nombre": "hack"}, format="json")
        self.assertEqual(r.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_metodo_delete_no_permitido(self):
        url = reverse("servicios-detail", kwargs={"id_servicio": "1"})
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class ServicioListViewTests(APITestCase):

    def test_lista_servicios_200_y_formato_lista(self):
        tipo = _make_tipo()
        _make_servicio("list-xyz", tipo=tipo, nombre="Hotel demo")
        response = self.client.get(reverse("servicios-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertTrue(
            any(item.get("id_servicio") == "list-xyz" for item in response.data)
        )
