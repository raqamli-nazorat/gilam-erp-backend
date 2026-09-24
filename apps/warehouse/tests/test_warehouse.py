from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.organization.models import Branch, Country, District, Organization, Region
from apps.warehouse.models import Warehouse


class WarehouseAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            phone_number="+998901112233",
            password="StrongPass123",
            full_name="Test Admin",
        )
        self.client.force_authenticate(self.user)

        self.country = Country.objects.create(name="O'zbekiston")
        self.region = Region.objects.create(name="Toshkent", country=self.country)
        self.district = District.objects.create(name="Chilonzor", region=self.region)
        self.organization = Organization.objects.create(
            name="Gilam Savdo",
            inn="123456789",
            region=self.region,
            district=self.district,
        )
        self.branch = Branch.objects.create(
            name="Chilonzor filiali",
            organization=self.organization,
            region=self.region,
            district=self.district,
        )
        self.warehouse = Warehouse.objects.create(
            branch=self.branch,
            name="Asosiy ombor",
            address="Chilonzor tumani, Bunyodkor ko'chasi 12A",
        )

    def test_list_warehouses_success(self):
        response = self.client.get("/api/v1/warehouse/warehouses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["branch_info"]["name"], "Chilonzor filiali"
        )

    def test_create_warehouse_success(self):
        response = self.client.post(
            "/api/v1/warehouse/warehouses/",
            {
                "branch": str(self.branch.id),
                "name": "Vitrina/Shourum",
                "address": "Chilonzor tumani, Bunyodkor ko'chasi 14",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Warehouse.objects.filter(name="Vitrina/Shourum").exists())

    def test_create_warehouse_invalid_data(self):
        response = self.client.post(
            "/api/v1/warehouse/warehouses/",
            {"address": "Filialsiz ombor"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_warehouses_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/warehouse/warehouses/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_warehouse_soft_delete(self):
        response = self.client.delete(
            f"/api/v1/warehouse/warehouses/{self.warehouse.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.warehouse.refresh_from_db()
        self.assertFalse(self.warehouse.is_active)
