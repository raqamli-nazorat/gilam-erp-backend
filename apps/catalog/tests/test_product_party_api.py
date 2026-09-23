from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import Design, ProductColor, ProductParty, Quality, Unit
from apps.organization.models import Branch, Country, District, Organization, Region


class ProductPartyAPITestCase(APITestCase):
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
        self.quality = Quality.objects.create(name="Lyuks")
        self.design = Design.objects.create(name="Naqsh 1", quality=self.quality)
        self.color = ProductColor.objects.create(name="Qizil", color_hex="#FF0000")
        self.unit = Unit.objects.create(name="m²")

        self.product_party = ProductParty.objects.create(
            branch=self.branch,
            name="1-partiya",
            party_number="P-001",
            quality=self.quality,
            design=self.design,
            color=self.color,
            unit=self.unit,
            price_per_sqm_purchase="100000.00",
            price_per_sqm_sale="150000.00",
        )

    def test_list_product_parties_success(self):
        response = self.client.get("/api/v1/catalog/product-parties/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        result = response.data["results"][0]
        self.assertEqual(result["design_info"]["name"], "Naqsh 1")
        self.assertEqual(result["branch_info"]["name"], "Chilonzor filiali")

    def test_create_product_party_success(self):
        response = self.client.post(
            "/api/v1/catalog/product-parties/",
            {
                "branch": str(self.branch.id),
                "name": "2-partiya",
                "quality": str(self.quality.id),
                "design": str(self.design.id),
                "color": str(self.color.id),
                "unit": str(self.unit.id),
                "price_per_sqm_purchase": "90000.00",
                "price_per_sqm_sale": "140000.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ProductParty.objects.filter(name="2-partiya").exists())

    def test_create_product_party_invalid_data(self):
        response = self.client.post(
            "/api/v1/catalog/product-parties/",
            {"name": "Nosoz partiya"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_party_duplicate_barcode_invalid_data(self):
        self.product_party.barcode = "123456"
        self.product_party.save()

        response = self.client.post(
            "/api/v1/catalog/product-parties/",
            {
                "branch": str(self.branch.id),
                "name": "3-partiya",
                "quality": str(self.quality.id),
                "design": str(self.design.id),
                "color": str(self.color.id),
                "unit": str(self.unit.id),
                "barcode": "123456",
                "price_per_sqm_purchase": "90000.00",
                "price_per_sqm_sale": "140000.00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_product_party_soft_delete(self):
        response = self.client.delete(
            f"/api/v1/catalog/product-parties/{self.product_party.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.product_party.refresh_from_db()
        self.assertFalse(self.product_party.is_active)
        list_response = self.client.get("/api/v1/catalog/product-parties/")
        self.assertEqual(list_response.data["count"], 0)

    def test_list_product_parties_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/catalog/product-parties/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
