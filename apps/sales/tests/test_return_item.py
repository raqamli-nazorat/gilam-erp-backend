from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Design, ProductColor, ProductParty, Quality, Unit
from apps.organization.models import Branch, Country, District, Organization, Region
from apps.sales.models import Customer, Order, OrderItem, ReturnItem, ReturnOrder
from apps.warehouse.models import Warehouse


class ReturnItemAPITestCase(APITestCase):
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
        self.customer = Customer.objects.create(
            organization=self.organization, full_name="Aliyev Vali"
        )
        self.order = Order.objects.create(
            organization=self.organization,
            branch=self.branch,
            customer=self.customer,
            seller=self.user,
            total_amount="500000.00",
            final_amount="500000.00",
            payment_status=Order.PaymentStatus.PAID,
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
        self.order_item = OrderItem.objects.create(
            order=self.order,
            product_party=self.product_party,
            warehouse=self.warehouse,
            width="2.00",
            length="3.00",
            sqm="6.00",
            price_per_sqm="420000.00",
            item_subtotal="2520000.00",
            final_item_price="2520000.00",
        )
        self.return_order = ReturnOrder.objects.create(
            organization=self.organization,
            branch=self.branch,
            order=self.order,
            customer=self.customer,
            refund_amount="150000.00",
        )
        self.return_item = ReturnItem.objects.create(
            return_order=self.return_order,
            order_item=self.order_item,
            restock_status=ReturnItem.RestockStatus.RESTOCKED,
        )

    def test_list_return_items_success(self):
        response = self.client.get("/api/v1/sales/return-items/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["restock_status"], "restocked")

    def test_create_return_item_success(self):
        response = self.client.post(
            "/api/v1/sales/return-items/",
            {
                "return_order": str(self.return_order.id),
                "order_item": str(self.order_item.id),
                "restock_status": ReturnItem.RestockStatus.DAMAGED_SCRAP,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReturnItem.objects.count(), 2)

    def test_create_return_item_invalid_data(self):
        response = self.client.post(
            "/api/v1/sales/return-items/", {"quantity": 1}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_return_items_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/sales/return-items/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
