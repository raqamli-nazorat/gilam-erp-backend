from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Design, ProductColor, ProductParty, Quality, Unit
from apps.organization.models import Branch, Country, District, Organization, Region
from apps.procurement.models import (
    Supplier,
    SupplierPurchase,
    SupplierPurchaseItem,
)
from apps.warehouse.models import Warehouse


class SupplierPurchaseItemAPITestCase(APITestCase):
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
            total_amount="31000000.00",
        )
        self.quality = Quality.objects.create(name="Lyuks")
        self.design = Design.objects.create(name="Naqsh 1", quality=self.quality)
        self.color = ProductColor.objects.create(name="Bej")
        self.unit = Unit.objects.create(name="m²")
        self.product_party = ProductParty.objects.create(
            branch=self.branch,
            name="AKTUEL 1247, bej",
            quality=self.quality,
            design=self.design,
            color=self.color,
            unit=self.unit,
            price_per_sqm_purchase="310000.00",
            price_per_sqm_sale="420000.00",
        )
        self.item = SupplierPurchaseItem.objects.create(
            purchase=self.purchase,
            product_party=self.product_party,
            roll_number="RL-20514",
            width="4.00",
            length="25.00",
            total_length_meters="100.00",
            price_per_sqm="310000.00",
            subtotal="31000000.00",
        )

    def test_list_supplier_purchase_items_success(self):
        response = self.client.get("/api/v1/procurement/purchase-items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["roll_number"], "RL-20514")

    def test_create_supplier_purchase_item_success(self):
        response = self.client.post(
            "/api/v1/procurement/purchase-items/",
            {
                "purchase": str(self.purchase.id),
                "product_party": str(self.product_party.id),
                "roll_number": "RL-20513",
                "width": "4.00",
                "length": "25.00",
                "price_per_sqm": "310000.00",
                "subtotal": "31000000.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(SupplierPurchaseItem.objects.count(), 2)

    def test_create_supplier_purchase_item_invalid_data(self):
        response = self.client.post(
            "/api/v1/procurement/purchase-items/",
            {"roll_number": "RL-99999"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_supplier_purchase_items_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/procurement/purchase-items/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
