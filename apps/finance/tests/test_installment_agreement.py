from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.finance.models import InstallmentAgreement
from apps.organization.models import Branch, Country, District, Organization, Region
from apps.sales.models import Customer, Order


class InstallmentAgreementAPITestCase(APITestCase):
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
            total_amount="1200000.00",
            final_amount="1200000.00",
            payment_status=Order.PaymentStatus.PARTIALLY_PAID,
        )
        self.agreement = InstallmentAgreement.objects.create(
            organization=self.organization,
            order=self.order,
            customer=self.customer,
            agreement_number="ST-0001",
            total_amount="1200000.00",
            down_payment="200000.00",
            remaining_amount="1000000.00",
            number_of_months=6,
        )

    def test_list_installment_agreements_success(self):
        response = self.client.get("/api/v1/finance/installment-agreements/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["agreement_number"], "ST-0001")

    def test_create_installment_agreement_success(self):
        other_order = Order.objects.create(
            organization=self.organization,
            branch=self.branch,
            customer=self.customer,
            seller=self.user,
            total_amount="900000.00",
            final_amount="900000.00",
            payment_status=Order.PaymentStatus.PARTIALLY_PAID,
        )
        response = self.client.post(
            "/api/v1/finance/installment-agreements/",
            {
                "organization": str(self.organization.id),
                "order": str(other_order.id),
                "customer": str(self.customer.id),
                "agreement_number": "ST-0002",
                "total_amount": "900000.00",
                "down_payment": "150000.00",
                "remaining_amount": "750000.00",
                "number_of_months": 3,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InstallmentAgreement.objects.count(), 2)

    def test_create_installment_agreement_invalid_data(self):
        response = self.client.post(
            "/api/v1/finance/installment-agreements/",
            {"agreement_number": "ST-0002"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_installment_agreement_duplicate_order_invalid_data(self):
        response = self.client.post(
            "/api/v1/finance/installment-agreements/",
            {
                "organization": str(self.organization.id),
                "order": str(self.order.id),
                "customer": str(self.customer.id),
                "agreement_number": "ST-0003",
                "total_amount": "1200000.00",
                "down_payment": "200000.00",
                "remaining_amount": "1000000.00",
                "number_of_months": 6,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_installment_agreements_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/finance/installment-agreements/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
