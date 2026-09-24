from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Design, ProductColor, ProductParty, Quality, Unit
from apps.organization.models import Branch, Country, District, Organization, Region
from apps.warehouse.models import CarpetRoll, Warehouse


class CarpetRollAPITestCase(APITestCase):
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
        self.unit = Unit.objects.create(name="m")
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
        self.carpet_roll = CarpetRoll.objects.create(
            product_party=self.product_party,
            warehouse=self.warehouse,
            roll_number="RL-0001",
            initial_length_meters="30.00",
            current_length_meters="30.00",
        )

    def test_list_carpet_rolls_success(self):
        response = self.client.get("/api/v1/warehouse/carpet-rolls/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        result = response.data["results"][0]
        self.assertEqual(result["roll_number"], "RL-0001")
        self.assertEqual(result["status"], CarpetRoll.Status.ACTIVE)

    def test_create_carpet_roll_success(self):
        response = self.client.post(
            "/api/v1/warehouse/carpet-rolls/",
            {
                "product_party": str(self.product_party.id),
                "warehouse": str(self.warehouse.id),
                "roll_number": "RL-0002",
                "initial_length_meters": "25.00",
                "current_length_meters": "25.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CarpetRoll.objects.filter(roll_number="RL-0002").exists())

    def test_create_carpet_roll_invalid_data(self):
        response = self.client.post(
            "/api/v1/warehouse/carpet-rolls/",
            {"roll_number": "RL-0003"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_carpet_rolls_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/warehouse/carpet-rolls/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
