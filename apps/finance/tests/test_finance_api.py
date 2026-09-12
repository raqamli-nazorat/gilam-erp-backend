from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.finance.models import CounterpartyType


class CounterpartyTypeAPITestCase(APITestCase):

    def setUp(self):
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
        response = self.client.get("/api/v1/finance/counterparty-types/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_counterparty_type_success(self):
        response = self.client.post(
            "/api/v1/finance/counterparty-types/",
            {"name": "Xaridor"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CounterpartyType.objects.filter(name="Xaridor").exists())

    def test_create_counterparty_type_invalid_data(self):
        response = self.client.post(
            "/api/v1/finance/counterparty-types/", {}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_counterparty_type_soft_delete(self):
        response = self.client.delete(
            f"/api/v1/finance/counterparty-types/{self.counterparty_type.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.counterparty_type.refresh_from_db()
        self.assertFalse(self.counterparty_type.is_active)
        list_response = self.client.get("/api/v1/finance/counterparty-types/")
        self.assertEqual(list_response.data["count"], 0)

    def test_list_counterparty_types_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/finance/counterparty-types/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
