from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

def _jwt(client):
    client.post(
        reverse("auth-register"),
        {"email": "geo@example.com", "password": "secret123", "name": "G"},
        format="json",
    )
    log = client.post(
        reverse("auth-login"),
        {"email": "geo@example.com", "password": "secret123"},
        format="json",
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {log.data['access']}")


class GeocodeApiTests(APITestCase):
    def test_geocode_sin_auth_401(self):
        r = self.client.get(reverse("auth-geocode"), {"q": "Madrid centro"})
        self.assertIn(r.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))

    def test_geocode_query_muy_corta_400(self):
        _jwt(self.client)
        r = self.client.get(reverse("auth-geocode"), {"q": "ab"})
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
