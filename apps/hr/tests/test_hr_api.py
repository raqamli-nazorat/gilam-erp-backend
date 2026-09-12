from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.hr.models import Position


class PositionAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            phone_number="+998901112233",
            password="StrongPass123",
            full_name="Test Admin",
        )
        self.client.force_authenticate(self.user)
        self.position = Position.objects.create(name="Direktor")

    def test_list_positions_success(self):
        response = self.client.get("/api/v1/hr/positions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_position_success(self):
        response = self.client.post(
            "/api/v1/hr/positions/",
            {"name": "Sotuvchi", "description": "Savdo maslahatchisi"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Position.objects.filter(name="Sotuvchi").exists())

    def test_create_position_invalid_data(self):
        response = self.client.post("/api/v1/hr/positions/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_position_soft_delete(self):
        response = self.client.delete(f"/api/v1/hr/positions/{self.position.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.position.refresh_from_db()
        self.assertFalse(self.position.is_active)
        list_response = self.client.get("/api/v1/hr/positions/")
        self.assertEqual(list_response.data["count"], 1)
        self.assertFalse(list_response.data["results"][0]["status"])

    def test_list_positions_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/hr/positions/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
