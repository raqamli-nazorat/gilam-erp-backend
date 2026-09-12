"""
Finance app ma'lumotnoma (CounterpartyType) CRUD endpointi uchun testlar.
"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.finance.models import CounterpartyType


class CounterpartyTypeAPITestCase(APITestCase):
    """Kontragent turlari endpointi testi."""

    def setUp(self):
        """Superuser va bitta namunaviy kontragent turini tayyorlaydi."""
        self.user = User.objects.create_superuser(
            phone_number="+998901112233",
            password="StrongPass123",
            full_name="Test Admin",
        )
        self.client.force_authenticate(self.user)
        self.counterparty_type = CounterpartyType.objects.create(
            name="Yetkazib beruvchi"
        )

    def test_list_counterparty_types_success(self):
        """GET /counterparty-types/ — 200 va yaratilgan yozuv ro'yxatda bo'ladi."""
        response = self.client.get("/api/v1/finance/counterparty-types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_counterparty_type_success(self):
        """POST /counterparty-types/ — 201 va yozuv bazada yaratiladi."""
        response = self.client.post(
            "/api/v1/finance/counterparty-types/",
            {"name": "Xaridor"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CounterpartyType.objects.filter(name="Xaridor").exists())

    def test_create_counterparty_type_invalid_data(self):
        """POST /counterparty-types/ — `name` bo'lmasa 400."""
        response = self.client.post(
            "/api/v1/finance/counterparty-types/", {}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_counterparty_type_soft_delete(self):
        """DELETE /counterparty-types/{id}/ — 204, yozuv nofaol bo'ladi, ro'yxatda qoladi."""
        response = self.client.delete(
            f"/api/v1/finance/counterparty-types/{self.counterparty_type.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.counterparty_type.refresh_from_db()
        self.assertFalse(self.counterparty_type.is_active)
        list_response = self.client.get("/api/v1/finance/counterparty-types/")
        self.assertEqual(list_response.data["count"], 1)
        self.assertFalse(list_response.data["results"][0]["status"])

    def test_list_counterparty_types_unauthenticated(self):
        """Autentifikatsiyasiz so'rov — 401."""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/finance/counterparty-types/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
