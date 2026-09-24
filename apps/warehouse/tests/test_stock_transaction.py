from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Design, ProductColor, ProductParty, Quality, Unit
from apps.organization.models import Branch, Country, District, Organization, Region
from apps.warehouse.models import StockTransaction, Warehouse


class StockTransactionAPITestCase(APITestCase):
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
        self.stock_transaction = StockTransaction.objects.create(
            organization=self.organization,
            product_party=self.product_party,
            to_warehouse=self.warehouse,
            transaction_type=StockTransaction.TransactionType.IN,
            quantity=10,
            ref_type=StockTransaction.RefType.PURCHASE,
        )

    def test_list_stock_transactions_success(self):
        response = self.client.get("/api/v1/warehouse/stock-transactions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["transaction_type"],
            StockTransaction.TransactionType.IN,
        )

    def test_create_stock_transaction_success(self):
        response = self.client.post(
            "/api/v1/warehouse/stock-transactions/",
            {
                "organization": str(self.organization.id),
                "product_party": str(self.product_party.id),
                "from_warehouse": str(self.warehouse.id),
                "transaction_type": StockTransaction.TransactionType.OUT,
                "quantity": 2,
                "ref_type": StockTransaction.RefType.SALE,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            StockTransaction.objects.filter(
                transaction_type=StockTransaction.TransactionType.OUT
            ).exists()
        )

    def test_create_stock_transaction_invalid_data(self):
        response = self.client.post(
            "/api/v1/warehouse/stock-transactions/",
            {"quantity": 2},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_stock_transactions_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/warehouse/stock-transactions/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
