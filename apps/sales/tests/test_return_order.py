from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.organization.models import Branch, Country, District, Organization, Region
from apps.sales.models import Customer, Order, ReturnOrder


class ReturnOrderAPITestCase(APITestCase):
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
        self.return_order = ReturnOrder.objects.create(
            organization=self.organization,
            branch=self.branch,
            order=self.order,
            customer=self.customer,
            refund_amount="150000.00",
            reason="Sifatsiz mahsulot",
        )

    def test_list_return_orders_success(self):
        response = self.client.get("/api/v1/sales/return-orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["refund_amount"], "150000.00")

    def test_create_return_order_success(self):
        response = self.client.post(
            "/api/v1/sales/return-orders/",
            {
                "organization": str(self.organization.id),
                "branch": str(self.branch.id),
                "order": str(self.order.id),
                "customer": str(self.customer.id),
                "refund_amount": "50000.00",
                "reason": "Noto'g'ri o'lcham",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ReturnOrder.objects.count(), 2)

    def test_create_return_order_invalid_data(self):
        response = self.client.post(
            "/api/v1/sales/return-orders/", {"reason": "Sabab"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_return_orders_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/sales/return-orders/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
