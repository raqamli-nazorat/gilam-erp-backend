from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.organization.models import Country, District, Organization, Region
from apps.procurement.models import Supplier


class SupplierAPITestCase(APITestCase):
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
        self.supplier = Supplier.objects.create(
            organization=self.organization,
            name="«SAMARQAND TEKS» MCHJ",
            phone="+998662334010",
        )

    def test_list_suppliers_success(self):
        response = self.client.get("/api/v1/procurement/suppliers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["organization_info"]["name"], "Gilam Savdo"
        )

    def test_create_supplier_success(self):
        response = self.client.post(
            "/api/v1/procurement/suppliers/",
            {
                "organization": str(self.organization.id),
                "name": "«TURON KARPET» MCHJ",
                "phone": "+998901234567",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Supplier.objects.filter(name="«TURON KARPET» MCHJ").exists())

    def test_create_supplier_invalid_data(self):
        response = self.client.post(
            "/api/v1/procurement/suppliers/", {"phone": "+998901234567"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_suppliers_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/procurement/suppliers/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
