from django.test import SimpleTestCase
from django.urls import NoReverseMatch, reverse


class NamedUrlResolveTests(SimpleTestCase):
    def test_auth_y_catalogo_publico_reversan(self):
        reverse("auth-register")
        reverse("auth-login")
        reverse("auth-refresh")
        reverse("auth-logout")
        reverse("auth-me")
        reverse("auth-change-password")
        reverse("auth-seller")
        reverse("servicios-list")
        reverse("servicios-detail", kwargs={"id_servicio": "_placeholder_"})
        reverse("servicios-resenas", kwargs={"id_servicio": "_x_"})

    def test_auth_protegido_reversan(self):
        reverse("auth-mis-servicios")
        reverse("auth-mis-servicios-update", kwargs={"id_servicio": "x"})
        reverse("auth-servicio-reserva-estado", kwargs={"id_servicio": "x", "pk": 1})
        reverse("auth-servicio-reservas", kwargs={"id_servicio": "x"})
        reverse("auth-mis-reservas")
        reverse("auth-reserva-detail", kwargs={"pk": 1})
        reverse("auth-mis-planes")
        reverse("auth-plan-detail", kwargs={"pk": 1})
        reverse("auth-plan-items", kwargs={"pk": 1})
        reverse("auth-plan-item-detail", kwargs={"pk": 1, "item_pk": 1})
        reverse("tipos-servicio")
        reverse("auth-geocode")

    def test_rutas_inexistentes_lanzan(self):
        with self.assertRaises(NoReverseMatch):
            reverse("no-existe-esta-vista")
