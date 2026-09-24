from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.organization.models import Branch, Country, District, Organization, Region
from apps.sales.models import Customer, Order


class OrderAPITestCase(APITestCase):
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

    def test_list_orders_success(self):
        response = self.client.get("/api/v1/sales/orders/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["customer_info"]["full_name"], "Aliyev Vali"
        )

    def test_create_order_success(self):
        response = self.client.post(
            "/api/v1/sales/orders/",
            {
                "organization": str(self.organization.id),
                "branch": str(self.branch.id),
                "customer": str(self.customer.id),
                "seller": str(self.user.id),
                "total_amount": "300000.00",
                "final_amount": "300000.00",
                "payment_status": Order.PaymentStatus.UNPAID,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)

    def test_create_order_invalid_data(self):
        response = self.client.post(
            "/api/v1/sales/orders/", {"total_amount": "300000.00"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/sales/orders/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
