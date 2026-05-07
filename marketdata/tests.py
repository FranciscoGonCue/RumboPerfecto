from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import CatalogoServicio, DetalleActividad, TipoServicio


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
    """Tests para GET /api/servicios/<id>/"""

    def setUp(self):
        self.tipo = _make_tipo()
        self.servicio = _make_servicio("1", tipo=self.tipo, nombre="Senderismo en el Teide")

    # ------------------------------------------------------------------
    # Casos de éxito
    # ------------------------------------------------------------------

    def test_detalle_devuelve_200(self):
        url = reverse("servicios-detail", kwargs={"id_servicio": "1"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detalle_contiene_campos_esperados(self):
        url = reverse("servicios-detail", kwargs={"id_servicio": "1"})
        response = self.client.get(url)
        data = response.json()

        campos_requeridos = [
            "id_servicio", "nombre", "descripcion", "precio_base",
            "ciudad", "pais", "valoracion", "num_resenas",
            "detalle_alojamiento", "detalle_transporte",
            "detalle_restauracion", "detalle_actividad",
        ]
        for campo in campos_requeridos:
            self.assertIn(campo, data, msg=f"Campo '{campo}' no encontrado en la respuesta")

    def test_detalle_devuelve_datos_correctos(self):
        url = reverse("servicios-detail", kwargs={"id_servicio": "1"})
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(data["id_servicio"], "1")
        self.assertEqual(data["nombre"], "Senderismo en el Teide")
        self.assertEqual(data["ciudad"], "Madrid")
        self.assertEqual(data["pais"], "España")
        self.assertEqual(float(data["precio_base"]), 50.0)

    def test_detalle_es_publico_sin_autenticacion(self):
        """El endpoint no requiere token."""
        self.client.credentials()  # sin cabecera Authorization
        url = reverse("servicios-detail", kwargs={"id_servicio": "1"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_detalle_incluye_tipo_anidado(self):
        url = reverse("servicios-detail", kwargs={"id_servicio": "1"})
        data = self.client.get(url).json()
        self.assertIsNotNone(data["tipo"])
        self.assertEqual(data["tipo"]["nombre_tipo"], "Actividad")

    def test_detalle_incluye_detalle_actividad_anidado(self):
        DetalleActividad.objects.create(
            servicio=self.servicio,
            duracion_estimada=120,
            dificultad="Moderado",
            guia_incluido=True,
        )
        url = reverse("servicios-detail", kwargs={"id_servicio": "1"})
        data = self.client.get(url).json()

        self.assertIsNotNone(data["detalle_actividad"])
        self.assertEqual(data["detalle_actividad"]["duracion_estimada"], 120)
        self.assertEqual(data["detalle_actividad"]["dificultad"], "Moderado")
        self.assertTrue(data["detalle_actividad"]["guia_incluido"])

    def test_detalle_sin_detalle_actividad_devuelve_null(self):
        """Si el servicio no tiene detalle_actividad, el campo debe ser null."""
        url = reverse("servicios-detail", kwargs={"id_servicio": "1"})
        data = self.client.get(url).json()
        self.assertIsNone(data["detalle_actividad"])

    def test_multiples_servicios_devuelven_el_correcto(self):
        """Cada id devuelve únicamente su servicio, no otro."""
        _make_servicio("2", tipo=self.tipo, nombre="Kayak en las Cíes")
        _make_servicio("3", tipo=self.tipo, nombre="Ruta por Doñana")

        for id_s, nombre in [("1", "Senderismo en el Teide"), ("2", "Kayak en las Cíes"), ("3", "Ruta por Doñana")]:
            url = reverse("servicios-detail", kwargs={"id_servicio": id_s})
            data = self.client.get(url).json()
            self.assertEqual(data["nombre"], nombre)

    # ------------------------------------------------------------------
    # Casos de error
    # ------------------------------------------------------------------

    def test_id_inexistente_devuelve_404(self):
        url = reverse("servicios-detail", kwargs={"id_servicio": "9999"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_metodo_post_no_permitido(self):
        url = reverse("servicios-detail", kwargs={"id_servicio": "1"})
        response = self.client.post(url, {"nombre": "hack"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_metodo_delete_no_permitido(self):
        url = reverse("servicios-detail", kwargs={"id_servicio": "1"})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
