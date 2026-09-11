"""
Organization app CRUD endpointlari uchun API testlari.

Har ViewSet uchun kamida bitta `_success`, hamda `_unauthenticated` va
tashkilot yaratishda `_invalid_data` holatlari tekshiriladi.
"""

from django.test import TestCase
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
from apps.organization.services import (
    get_branch_status_counts,
    get_organization_status_counts,
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
        """DELETE /branches/{id}/ — 204, yozuv nofaol bo'ladi, lekin ro'yxatda qoladi."""
        response = self.client.delete(
            f"/api/v1/organization/branches/{self.branch.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.branch.refresh_from_db()
        self.assertFalse(self.branch.is_active)
        list_response = self.client.get("/api/v1/organization/branches/")
        self.assertEqual(list_response.data["count"], 1)
        self.assertFalse(list_response.data["results"][0]["status"])

    def test_list_branches_returns_status_and_warehouses_count(self):
        """GET /branches/ — `status` va `warehouses_count` maydonlari qaytadi."""
        response = self.client.get("/api/v1/organization/branches/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data["results"][0]
        self.assertTrue(result["status"])
        self.assertEqual(result["warehouses_count"], 0)

    def test_list_branches_filters_by_status(self):
        """GET /branches/?status=false — faqat yopilgan filiallarni qaytaradi."""
        inactive_branch = Branch.objects.create(
            name="Yopilgan filial",
            organization=self.organization,
            region=self.region,
            district=self.district,
        )
        inactive_branch.delete()

        response = self.client.get(
            "/api/v1/organization/branches/", {"status": "false"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["name"] for item in response.data["results"]]
        self.assertEqual(names, ["Yopilgan filial"])

    def test_branches_counts_action_returns_status_summary(self):
        """GET /branches/counts/ — faol va yopilgan filiallar sonini qaytaradi."""
        inactive_branch = Branch.objects.create(
            name="Yopilgan filial",
            organization=self.organization,
            region=self.region,
            district=self.district,
        )
        inactive_branch.delete()

        response = self.client.get("/api/v1/organization/branches/counts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"active": 1, "inactive": 1})

    def test_retrieve_organization_success_returns_branches_count_and_status(self):
        """GET /organizations/{id}/ — faqat faol filiallar soni va holat qaytadi."""
        inactive_branch = Branch.objects.create(
            name="Yopilgan filial",
            organization=self.organization,
            region=self.region,
            district=self.district,
        )
        inactive_branch.delete()

        response = self.client.get(
            f"/api/v1/organization/organizations/{self.organization.id}/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["branches_count"], 1)
        self.assertTrue(response.data["status"])

    def test_list_organizations_filters_by_status(self):
        """GET /organizations/?status=false — faqat to'xtatilgan tashkilotlarni qaytaradi."""
        inactive_organization = Organization.objects.create(
            name="To'xtatilgan Tashkilot",
            inn="222222222",
            region=self.region,
            district=self.district,
        )
        inactive_organization.delete()

        response = self.client.get(
            "/api/v1/organization/organizations/", {"status": "false"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["name"] for item in response.data["results"]]
        self.assertEqual(names, ["To'xtatilgan Tashkilot"])

    def test_counts_action_returns_status_summary(self):
        """GET /organizations/counts/ — faol va to'xtatilgan tashkilotlar sonini qaytaradi."""
        inactive_organization = Organization.objects.create(
            name="To'xtatilgan Tashkilot",
            inn="333333333",
            region=self.region,
            district=self.district,
        )
        inactive_organization.delete()

        response = self.client.get("/api/v1/organization/organizations/counts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"active": 1, "inactive": 1})

    def test_list_unauthenticated(self):
        """Autentifikatsiyasiz so'rov — 401."""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/organization/organizations/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class OrganizationServiceTestCase(TestCase):
    """`get_organization_status_counts` servis funksiyasi testi."""

    def setUp(self):
        """Lokatsiya ma'lumotnoma yozuvlarini tayyorlaydi."""
        self.country = Country.objects.create(name="O'zbekiston")
        self.region = Region.objects.create(name="Toshkent", country=self.country)
        self.district = District.objects.create(name="Chilonzor", region=self.region)

    def test_get_organization_status_counts_returns_correct_totals(self):
        """Faol va to'xtatilgan tashkilotlar sonini to'g'ri hisoblaydi."""
        Organization.objects.create(
            name="Faol 1", inn="111111111", region=self.region, district=self.district
        )
        Organization.objects.create(
            name="Faol 2", inn="444444444", region=self.region, district=self.district
        )
        inactive_organization = Organization.objects.create(
            name="Nofaol", inn="555555555", region=self.region, district=self.district
        )
        inactive_organization.delete()

        counts = get_organization_status_counts()

        self.assertEqual(counts, {"active": 2, "inactive": 1})


class BranchServiceTestCase(TestCase):
    """`get_branch_status_counts` servis funksiyasi testi."""

    def setUp(self):
        """Lokatsiya va tashkilot ma'lumotnoma yozuvlarini tayyorlaydi."""
        self.country = Country.objects.create(name="O'zbekiston")
        self.region = Region.objects.create(name="Toshkent", country=self.country)
        self.district = District.objects.create(name="Chilonzor", region=self.region)
        self.organization = Organization.objects.create(
            name="Gilam Savdo",
            inn="666666666",
            region=self.region,
            district=self.district,
        )

    def test_get_branch_status_counts_returns_correct_totals(self):
        """Faol va yopilgan filiallar sonini to'g'ri hisoblaydi."""
        Branch.objects.create(
            name="Faol 1",
            organization=self.organization,
            region=self.region,
            district=self.district,
        )
        inactive_branch = Branch.objects.create(
            name="Yopilgan 1",
            organization=self.organization,
            region=self.region,
            district=self.district,
        )
        inactive_branch.delete()

        counts = get_branch_status_counts()

        self.assertEqual(counts, {"active": 1, "inactive": 1})
