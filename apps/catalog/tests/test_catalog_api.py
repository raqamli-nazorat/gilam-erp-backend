from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.catalog.models import ProductColor, Quality, Unit


class CatalogReferenceAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            phone_number="+998901112233",
            password="StrongPass123",
            full_name="Test Admin",
        )
        self.client.force_authenticate(self.user)

        self.quality = Quality.objects.create(name="Lyuks", description="Ipak aralash")
        self.unit = Unit.objects.create(name="m²")
        self.color = ProductColor.objects.create(name="Qizil", color_hex="#FF0000")

    def test_list_qualities_success(self):
        response = self.client.get("/api/v1/catalog/qualities/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertTrue(response.data["results"][0]["status"])

    def test_create_quality_success(self):
        response = self.client.post(
            "/api/v1/catalog/qualities/",
            {"name": "Premium", "description": "1 500 000 tugun/m²"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Quality.objects.filter(name="Premium").exists())

    def test_create_quality_invalid_data(self):
        response = self.client.post(
            "/api/v1/catalog/qualities/", {"description": "Nomi yo'q"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_quality_soft_delete(self):
        response = self.client.delete(f"/api/v1/catalog/qualities/{self.quality.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.quality.refresh_from_db()
        self.assertFalse(self.quality.is_active)
        list_response = self.client.get("/api/v1/catalog/qualities/")
        self.assertEqual(list_response.data["count"], 1)
        self.assertFalse(list_response.data["results"][0]["status"])

    def test_list_qualities_filters_by_status(self):
        inactive_quality = Quality.objects.create(name="Ekonom")
        inactive_quality.delete()

        response = self.client.get("/api/v1/catalog/qualities/", {"status": "false"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["name"] for item in response.data["results"]]
        self.assertEqual(names, ["Ekonom"])

    def test_list_units_success(self):
        response = self.client.get("/api/v1/catalog/units/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_unit_invalid_data(self):
        response = self.client.post("/api/v1/catalog/units/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_colors_success_returns_color_hex(self):
        response = self.client.get("/api/v1/catalog/colors/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"][0]["color_hex"], "#FF0000")

    def test_create_color_success(self):
        response = self.client.post(
            "/api/v1/catalog/colors/",
            {"name": "Ko'k", "color_hex": "#0000FF"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ProductColor.objects.filter(name="Ko'k").exists())

    def test_list_qualities_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/catalog/qualities/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
