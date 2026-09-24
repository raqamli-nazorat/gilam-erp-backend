from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.organization.models import Country, District, Organization, Region
from apps.sales.models import Customer


class CustomerAPITestCase(APITestCase):
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
        self.customer = Customer.objects.create(
            organization=self.organization,
            full_name="Aliyev Vali",
            phone="+998901234567",
        )

    def test_list_customers_success(self):
        response = self.client.get("/api/v1/sales/customers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["full_name"], "Aliyev Vali")

    def test_create_customer_success(self):
        response = self.client.post(
            "/api/v1/sales/customers/",
            {
                "organization": str(self.organization.id),
                "full_name": "Karimova Nodira",
                "phone": "+998907778899",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Customer.objects.filter(full_name="Karimova Nodira").exists())

    def test_create_customer_invalid_data(self):
        response = self.client.post(
            "/api/v1/sales/customers/", {"phone": "+998907778899"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_customers_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/sales/customers/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
