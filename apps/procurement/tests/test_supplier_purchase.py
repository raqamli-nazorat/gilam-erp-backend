from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Design, ProductColor, ProductParty, Quality, Unit
from apps.organization.models import Branch, Country, District, Organization, Region
from apps.procurement.models import Supplier, SupplierPurchase, SupplierPurchaseItem
from apps.warehouse.models import CarpetRoll, ProductStock, StockTransaction, Warehouse


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

        self.quality = Quality.objects.create(name="AKTUEL")
        self.design = Design.objects.create(quality=self.quality, name="400X3000")
        self.color = ProductColor.objects.create(name="GRI / MAVI")
        self.unit = Unit.objects.create(name="kv.m")
        self.product_party = ProductParty.objects.create(
            branch=self.branch,
            name="Mavjud partiya",
            quality=self.quality,
            design=self.design,
            color=self.color,
            unit=self.unit,
            price_per_sqm_purchase="50000.00",
            price_per_sqm_sale="60000.00",
        )

    def test_list_supplier_purchases_success(self):
        response = self.client.get("/api/v1/procurement/purchases/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["supplier_info"]["name"],
            "«SAMARQAND TEKS» MCHJ",
        )

    def test_retrieve_supplier_purchase_includes_items_success(self):
        item = SupplierPurchaseItem.objects.create(
            purchase=self.purchase,
            product_party=self.product_party,
            width="4.00",
            length="30.00",
            price_per_sqm="50000.00",
            subtotal="6000000.00",
        )
        response = self.client.get(f"/api/v1/procurement/purchases/{self.purchase.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["items"]), 1)
        self.assertEqual(response.data["items"][0]["id"], str(item.id))
        self.assertEqual(
            response.data["items"][0]["product_party_info"]["name"],
            "Mavjud partiya",
        )

    def test_list_supplier_purchases_excludes_items(self):
        response = self.client.get("/api/v1/procurement/purchases/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("items", response.data["results"][0])

    def test_update_supplier_purchase_header_recalculates_debt_success(self):
        response = self.client.patch(
            f"/api/v1/procurement/purchases/{self.purchase.id}/",
            {"paid_amount": "50000000.00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["paid_amount"], "50000000.00")
        self.assertEqual(response.data["debt_amount"], "54480000.00")

    def test_update_supplier_purchase_status_is_ignored(self):
        """`status` `update`ga qo'shilmagan — faqat `confirm`/`revert` orqali o'zgaradi."""
        response = self.client.patch(
            f"/api/v1/procurement/purchases/{self.purchase.id}/",
            {"status": "confirmed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "draft")

    def test_confirm_supplier_purchase_success(self):
        SupplierPurchaseItem.objects.create(
            purchase=self.purchase,
            product_party=self.product_party,
            width="4.00",
            length="30.00",
            price_per_sqm="50000.00",
            subtotal="6000000.00",
        )
        response = self.client.post(
            f"/api/v1/procurement/purchases/{self.purchase.id}/confirm/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "confirmed")

        stock = ProductStock.objects.get(
            warehouse=self.warehouse, product_party=self.product_party
        )
        self.assertEqual(stock.quantity, 1)
        self.assertEqual(str(stock.total_length_meters), "30.00")
        self.assertEqual(
            StockTransaction.objects.filter(
                ref_type=StockTransaction.RefType.PURCHASE, ref_id=self.purchase.id
            ).count(),
            1,
        )

    def test_confirm_supplier_purchase_creates_carpet_roll_success(self):
        SupplierPurchaseItem.objects.create(
            purchase=self.purchase,
            product_party=self.product_party,
            roll_number="RL-001",
            width="4.00",
            length="30.00",
            price_per_sqm="50000.00",
            subtotal="6000000.00",
        )
        response = self.client.post(
            f"/api/v1/procurement/purchases/{self.purchase.id}/confirm/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        roll = CarpetRoll.objects.get(roll_number="RL-001")
        self.assertEqual(roll.warehouse_id, self.warehouse.id)
        self.assertEqual(str(roll.current_length_meters), "30.00")

    def test_confirm_supplier_purchase_without_items_invalid_data(self):
        response = self.client.post(
            f"/api/v1/procurement/purchases/{self.purchase.id}/confirm/"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_confirm_supplier_purchase_already_confirmed_invalid_data(self):
        SupplierPurchaseItem.objects.create(
            purchase=self.purchase,
            product_party=self.product_party,
            width="4.00",
            length="30.00",
            price_per_sqm="50000.00",
            subtotal="6000000.00",
        )
        self.client.post(f"/api/v1/procurement/purchases/{self.purchase.id}/confirm/")
        response = self.client.post(
            f"/api/v1/procurement/purchases/{self.purchase.id}/confirm/"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_revert_supplier_purchase_success(self):
        SupplierPurchaseItem.objects.create(
            purchase=self.purchase,
            product_party=self.product_party,
            width="4.00",
            length="30.00",
            price_per_sqm="50000.00",
            subtotal="6000000.00",
        )
        self.client.post(f"/api/v1/procurement/purchases/{self.purchase.id}/confirm/")

        response = self.client.post(
            f"/api/v1/procurement/purchases/{self.purchase.id}/revert/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "draft")

        stock = ProductStock.objects.get(
            warehouse=self.warehouse, product_party=self.product_party
        )
        self.assertEqual(stock.quantity, 0)

    def test_revert_supplier_purchase_not_confirmed_invalid_data(self):
        response = self.client.post(
            f"/api/v1/procurement/purchases/{self.purchase.id}/revert/"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_revert_supplier_purchase_blocked_when_roll_used_invalid_data(self):
        SupplierPurchaseItem.objects.create(
            purchase=self.purchase,
            product_party=self.product_party,
            roll_number="RL-002",
            width="4.00",
            length="30.00",
            price_per_sqm="50000.00",
            subtotal="6000000.00",
        )
        self.client.post(f"/api/v1/procurement/purchases/{self.purchase.id}/confirm/")

        roll = CarpetRoll.objects.get(roll_number="RL-002")
        roll.current_length_meters = "10.00"
        roll.save(update_fields=["current_length_meters"])

        response = self.client.post(
            f"/api/v1/procurement/purchases/{self.purchase.id}/revert/"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_purchase_with_existing_product_party_success(self):
        response = self.client.post(
            "/api/v1/procurement/purchases/",
            {
                "organization": str(self.organization.id),
                "supplier": str(self.supplier.id),
                "warehouse": str(self.warehouse.id),
                "items": [
                    {
                        "product_party": str(self.product_party.id),
                        "width": "4.00",
                        "length": "30.00",
                        "price_per_sqm": "50000.00",
                    }
                ],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["total_amount"], "6000000.00")
        self.assertEqual(len(response.data["items"]), 1)
        self.assertTrue(response.data["document_number"].startswith("KR-"))
        self.assertEqual(SupplierPurchaseItem.objects.count(), 1)

    def test_create_supplier_purchase_with_new_product_party_success(self):
        response = self.client.post(
            "/api/v1/procurement/purchases/",
            {
                "organization": str(self.organization.id),
                "supplier": str(self.supplier.id),
                "warehouse": str(self.warehouse.id),
                "items": [
                    {
                        "product_party_data": {
                            "name": "Yangi partiya",
                            "quality": str(self.quality.id),
                            "design": str(self.design.id),
                            "color": str(self.color.id),
                            "unit": str(self.unit.id),
                            "price_per_sqm_purchase": "50000.00",
                            "price_per_sqm_sale": "60000.00",
                        },
                        "width": "4.00",
                        "length": "30.00",
                        "price_per_sqm": "50000.00",
                    }
                ],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductParty.objects.count(), 2)
        self.assertEqual(SupplierPurchaseItem.objects.count(), 1)

    def test_create_supplier_purchase_invalid_data(self):
        response = self.client.post(
            "/api/v1/procurement/purchases/",
            {
                "organization": str(self.organization.id),
                "supplier": str(self.supplier.id),
                "warehouse": str(self.warehouse.id),
                "items": [],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_supplier_purchase_both_product_party_fields_invalid(self):
        response = self.client.post(
            "/api/v1/procurement/purchases/",
            {
                "organization": str(self.organization.id),
                "supplier": str(self.supplier.id),
                "warehouse": str(self.warehouse.id),
                "items": [
                    {
                        "product_party": str(self.product_party.id),
                        "product_party_data": {
                            "name": "X",
                            "quality": str(self.quality.id),
                            "design": str(self.design.id),
                            "color": str(self.color.id),
                            "unit": str(self.unit.id),
                            "price_per_sqm_purchase": "1.00",
                            "price_per_sqm_sale": "1.00",
                        },
                        "width": "4.00",
                        "length": "30.00",
                        "price_per_sqm": "50000.00",
                    }
                ],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_supplier_purchases_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/procurement/purchases/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
