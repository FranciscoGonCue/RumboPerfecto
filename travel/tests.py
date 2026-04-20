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
            {
                "email": "test@example.com",
                "password": "secret123",
            },
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")
        me_response = self.client.get(reverse("auth-me"))
        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["email"], "test@example.com")


class TripActivityApiTests(APITestCase):
    def setUp(self):
        register_response = self.client.post(
            reverse("auth-register"),
            {
                "email": "owner@example.com",
                "password": "secret123",
                "name": "Owner User",
            },
            format="json",
        )
        self.access = register_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")

    def test_trip_crud_and_activity_crud(self):
        create_trip_response = self.client.post(
            "/api/trips/",
            {
                "title": "Viaje a Madrid",
                "start_date": "2026-06-01",
                "end_date": "2026-06-03",
            },
            format="json",
        )
        self.assertEqual(create_trip_response.status_code, status.HTTP_201_CREATED)
        trip_id = create_trip_response.data["id"]

        create_activity_response = self.client.post(
            "/api/activities/",
            {
                "trip": trip_id,
                "day": 2,
                "title": "Museo del Prado",
                "location": "Madrid",
                "time": "10:30",
            },
            format="json",
        )
        self.assertEqual(create_activity_response.status_code, status.HTTP_201_CREATED)

        list_trips_response = self.client.get("/api/trips/")
        self.assertEqual(list_trips_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_trips_response.data["results"]), 1)
        self.assertEqual(len(list_trips_response.data["results"][0]["activities"]), 1)

        list_activities_response = self.client.get(f"/api/activities/?trip={trip_id}")
        self.assertEqual(list_activities_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_activities_response.data["results"]), 1)

        delete_trip_response = self.client.delete(f"/api/trips/{trip_id}/")
        self.assertEqual(delete_trip_response.status_code, status.HTTP_204_NO_CONTENT)

        list_after_delete_response = self.client.get("/api/trips/")
        self.assertEqual(len(list_after_delete_response.data["results"]), 0)

    def test_activity_day_must_be_within_trip_duration(self):
        create_trip_response = self.client.post(
            "/api/trips/",
            {
                "title": "Viaje corto",
                "start_date": "2026-07-10",
                "end_date": "2026-07-11",
            },
            format="json",
        )
        trip_id = create_trip_response.data["id"]

        bad_activity_response = self.client.post(
            "/api/activities/",
            {
                "trip": trip_id,
                "day": 3,
                "title": "Actividad fuera de rango",
                "location": "Valencia",
                "time": "14:00",
            },
            format="json",
        )
        self.assertEqual(bad_activity_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("day", bad_activity_response.data)
