from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.organization.models import Branch, Country, District, Organization, Region
from apps.procurement.models import Supplier, SupplierPurchase
from apps.warehouse.models import Warehouse


class SupplierPurchaseAPITestCase(APITestCase):
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
            name="Zavod filiali",
            organization=self.organization,
            region=self.region,
            district=self.district,
        )
        self.warehouse = Warehouse.objects.create(
            branch=self.branch, name="Zavod ombori"
        )
        self.supplier = Supplier.objects.create(
            organization=self.organization, name="«SAMARQAND TEKS» MCHJ"
        )
        self.purchase = SupplierPurchase.objects.create(
            organization=self.organization,
            supplier=self.supplier,
            warehouse=self.warehouse,
            total_amount="104480000.00",
            paid_amount="40000000.00",
            debt_amount="64480000.00",
        )

    def test_list_supplier_purchases_success(self):
        response = self.client.get("/api/v1/procurement/purchases/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["supplier_info"]["name"],
            "«SAMARQAND TEKS» MCHJ",
        )

    def test_create_supplier_purchase_success(self):
        response = self.client.post(
            "/api/v1/procurement/purchases/",
            {
                "organization": str(self.organization.id),
                "supplier": str(self.supplier.id),
                "warehouse": str(self.warehouse.id),
                "total_amount": "5000000.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SupplierPurchase.objects.count(), 2)

    def test_create_supplier_purchase_invalid_data(self):
        response = self.client.post(
            "/api/v1/procurement/purchases/",
            {"total_amount": "5000000.00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_supplier_purchases_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/procurement/purchases/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
