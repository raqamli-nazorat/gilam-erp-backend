from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.finance.models import InstallmentAgreement, InstallmentSchedule
from apps.organization.models import Branch, Country, District, Organization, Region
from apps.sales.models import Customer, Order


class InstallmentScheduleAPITestCase(APITestCase):
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
        self.schedule = InstallmentSchedule.objects.create(
            agreement=self.agreement,
            payment_number=1,
            due_date="2026-03-01",
            amount_to_pay="166666.00",
        )

    def test_list_installment_schedules_success(self):
        response = self.client.get("/api/v1/finance/installment-schedules/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["payment_number"], 1)

    def test_create_installment_schedule_success(self):
        response = self.client.post(
            "/api/v1/finance/installment-schedules/",
            {
                "agreement": str(self.agreement.id),
                "payment_number": 2,
                "due_date": "2026-04-01",
                "amount_to_pay": "166666.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(InstallmentSchedule.objects.count(), 2)

    def test_create_installment_schedule_invalid_data(self):
        response = self.client.post(
            "/api/v1/finance/installment-schedules/",
            {"payment_number": 2},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_installment_schedules_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/finance/installment-schedules/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
