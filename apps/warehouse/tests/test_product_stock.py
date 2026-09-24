from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Design, ProductColor, ProductParty, Quality, Unit
from apps.organization.models import Branch, Country, District, Organization, Region
from apps.warehouse.models import ProductStock, Warehouse


class ProductStockAPITestCase(APITestCase):
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
            branch=self.branch, name="Asosiy ombor"
        )
        self.quality = Quality.objects.create(name="Lyuks")
        self.design = Design.objects.create(name="Naqsh 1", quality=self.quality)
        self.color = ProductColor.objects.create(name="Qizil")
        self.unit = Unit.objects.create(name="dona")
        self.product_party = ProductParty.objects.create(
            branch=self.branch,
            name="1-partiya",
            quality=self.quality,
            design=self.design,
            color=self.color,
            unit=self.unit,
            price_per_sqm_purchase="100000.00",
            price_per_sqm_sale="150000.00",
        )
        self.product_stock = ProductStock.objects.create(
            warehouse=self.warehouse,
            product_party=self.product_party,
            quantity=10,
        )

    def test_list_product_stocks_success(self):
        response = self.client.get("/api/v1/warehouse/product-stocks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["quantity"], 10)

    def test_create_product_stock_success(self):
        other_warehouse = Warehouse.objects.create(
            branch=self.branch, name="Ikkinchi ombor"
        )
        response = self.client.post(
            "/api/v1/warehouse/product-stocks/",
            {
                "warehouse": str(other_warehouse.id),
                "product_party": str(self.product_party.id),
                "quantity": 5,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ProductStock.objects.filter(warehouse=other_warehouse).exists())

    def test_create_product_stock_duplicate_invalid_data(self):
        response = self.client.post(
            "/api/v1/warehouse/product-stocks/",
            {
                "warehouse": str(self.warehouse.id),
                "product_party": str(self.product_party.id),
                "quantity": 3,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_product_stocks_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/warehouse/product-stocks/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
