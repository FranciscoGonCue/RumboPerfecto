from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class AuthApiTests(APITestCase):
    def test_register_login_and_me(self):
        register_response = self.client.post(
            reverse("auth-register"),
            {
                "email": "test@example.com",
                "password": "secret123",
                "name": "Test User",
            },
            format="json",
        )
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", register_response.data)
        self.assertIn("refresh", register_response.data)

        login_response = self.client.post(
            reverse("auth-login"),
            {"email": "test@example.com", "password": "secret123"},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}"
        )
        me_response = self.client.get(reverse("auth-me"))
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["email"], "test@example.com")


class RegisterValidationTests(APITestCase):
    def test_email_duplicado_devuelve_400(self):
        payload = {
            "email": "dup@example.com",
            "password": "secret123",
            "name": "Uno",
        }
        r1 = self.client.post(reverse("auth-register"), payload, format="json")
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED)
        r2 = self.client.post(reverse("auth-register"), payload, format="json")
        self.assertEqual(r2.status_code, status.HTTP_400_BAD_REQUEST)


class LogoutApiTests(APITestCase):
    def test_logout_rechaza_refresh_invalido(self):
        reg = self.client.post(
            reverse("auth-register"),
            {
                "email": "out@example.com",
                "password": "secret123",
                "name": "Out User",
            },
            format="json",
        )
        self.assertEqual(reg.status_code, status.HTTP_201_CREATED)
        access = reg.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        out = self.client.post(
            reverse("auth-logout"),
            {"refresh": "token-falso"},
            format="json",
        )
        self.assertEqual(out.status_code, status.HTTP_400_BAD_REQUEST)


class TokenRefreshTests(APITestCase):
    def test_refresh_devuelve_nuevo_access(self):
        reg = self.client.post(
            reverse("auth-register"),
            {
                "email": "ref@example.com",
                "password": "secret123",
                "name": "Ref User",
            },
            format="json",
        )
        self.assertEqual(reg.status_code, status.HTTP_201_CREATED)
        refresh = reg.data["refresh"]
        r = self.client.post(reverse("auth-refresh"), {"refresh": refresh}, format="json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("access", r.data)
