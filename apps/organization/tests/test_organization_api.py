"""
Organization app CRUD endpointlari uchun API testlari.

Har ViewSet uchun kamida bitta `_success`, hamda `_unauthenticated` va
tashkilot yaratishda `_invalid_data` holatlari tekshiriladi.
"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User
from apps.organization.models import (
    Branch,
    Country,
    District,
    Organization,
    Region,
)


class OrganizationAPITestCase(APITestCase):
    """Country/Region/District/Organization/Branch endpointlari testi."""

    def setUp(self):
        """Superuser va bazaviy ma'lumotnoma yozuvlarini tayyorlaydi."""
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

    def test_list_countries_success(self):
        """GET /countries/ — 200 va ro'yxatda mavjud davlat qaytadi."""
        response = self.client.get("/api/v1/organization/countries/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_list_regions_success(self):
        """GET /regions/ — 200 va nested `country_info` qaytadi."""
        response = self.client.get("/api/v1/organization/regions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["results"][0]["country_info"]["name"], "O'zbekiston"
        )

    def test_list_districts_success(self):
        """GET /districts/ — 200."""
        response = self.client.get("/api/v1/organization/districts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_region_success(self):
        """POST /regions/ — 201 va yozuv bazada yaratiladi."""
        response = self.client.post(
            "/api/v1/organization/regions/",
            {"name": "Samarqand", "country": str(self.country.id)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Region.objects.filter(name="Samarqand").exists())

    def test_create_organization_success(self):
        """POST /organizations/ — 201."""
        response = self.client.post(
            "/api/v1/organization/organizations/",
            {
                "name": "Yangi Tashkilot",
                "inn": "987654321",
                "region": str(self.region.id),
                "district": str(self.district.id),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["region_info"]["name"], "Toshkent")

    def test_create_branch_success(self):
        """POST /branches/ — 201."""
        response = self.client.post(
            "/api/v1/organization/branches/",
            {
                "name": "Yunusobod filiali",
                "organization": str(self.organization.id),
                "region": str(self.region.id),
                "district": str(self.district.id),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Branch.objects.count(), 2)

    def test_create_organization_invalid_data(self):
        """POST /organizations/ — majburiy `inn` va `region` yo'q bo'lsa 400."""
        response = self.client.post(
            "/api/v1/organization/organizations/", {"name": "Nosoz"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_branch_soft_delete(self):
        """DELETE /branches/{id}/ — 204 va yozuv ro'yxatdan yo'qoladi (soft delete)."""
        response = self.client.delete(
            f"/api/v1/organization/branches/{self.branch.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.branch.refresh_from_db()
        self.assertFalse(self.branch.is_active)
        list_response = self.client.get("/api/v1/organization/branches/")
        self.assertEqual(list_response.data["count"], 0)

    def test_list_unauthenticated(self):
        """Autentifikatsiyasiz so'rov — 401."""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/organization/organizations/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
