from django.contrib.auth.models import Permission
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User
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

    def test_list_countries_success(self):
        response = self.client.get("/api/v1/organization/countries/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_list_regions_success(self):
        response = self.client.get("/api/v1/organization/regions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["results"][0]["country_info"]["name"], "O'zbekiston"
        )

    def test_list_districts_success(self):
        response = self.client.get("/api/v1/organization/districts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_region_success(self):
        response = self.client.post(
            "/api/v1/organization/regions/",
            {"name": "Samarqand", "country": str(self.country.id)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Region.objects.filter(name="Samarqand").exists())

    def test_create_organization_success(self):
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
        response = self.client.post(
            "/api/v1/organization/organizations/", {"name": "Nosoz"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_branch_soft_delete(self):
        response = self.client.delete(
            f"/api/v1/organization/branches/{self.branch.id}/"
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.branch.refresh_from_db()
        self.assertFalse(self.branch.is_active)
        list_response = self.client.get("/api/v1/organization/branches/")
        self.assertEqual(list_response.data["count"], 0)

    def test_list_branches_returns_warehouses_count(self):
        response = self.client.get("/api/v1/organization/branches/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.data["results"][0]
        self.assertEqual(result["warehouses_count"], 0)

    def test_list_branches_excludes_inactive(self):
        inactive_branch = Branch.objects.create(
            name="Yopilgan filial",
            organization=self.organization,
            region=self.region,
            district=self.district,
        )
        inactive_branch.delete()

        response = self.client.get("/api/v1/organization/branches/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["name"] for item in response.data["results"]]
        self.assertNotIn("Yopilgan filial", names)

    def test_branches_counts_action_returns_status_summary(self):
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

    def test_retrieve_organization_success_returns_branches_count(self):
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

    def test_list_organizations_excludes_inactive(self):
        inactive_organization = Organization.objects.create(
            name="To'xtatilgan Tashkilot",
            inn="222222222",
            region=self.region,
            district=self.district,
        )
        inactive_organization.delete()

        response = self.client.get("/api/v1/organization/organizations/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        names = [item["name"] for item in response.data["results"]]
        self.assertNotIn("To'xtatilgan Tashkilot", names)

    def test_counts_action_returns_status_summary(self):
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
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/organization/organizations/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_suspend_organization_success_by_system_admin(self):
        response = self.client.patch(
            f"/api/v1/organization/organizations/{self.organization.id}/suspend/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.organization.refresh_from_db()
        self.assertFalse(self.organization.is_active)
        self.assertFalse(response.data["is_active"])

    def test_activate_organization_success_by_system_admin(self):
        self.organization.is_active = False
        self.organization.save()

        response = self.client.patch(
            f"/api/v1/organization/organizations/{self.organization.id}/activate/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.organization.refresh_from_db()
        self.assertTrue(self.organization.is_active)
        self.assertTrue(response.data["is_active"])

    def test_suspend_organization_forbidden_for_regular_user(self):
        regular_user = User.objects.create_user(
            phone_number="+998909998877",
            password="StrongPass123",
            full_name="Branch Manager",
            organization=self.organization,
            branch=self.branch,
        )
        self.client.force_authenticate(regular_user)

        response = self.client.patch(
            f"/api/v1/organization/organizations/{self.organization.id}/suspend/"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_close_branch_success_by_system_admin(self):
        response = self.client.patch(
            f"/api/v1/organization/branches/{self.branch.id}/close/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.branch.refresh_from_db()
        self.assertFalse(self.branch.is_active)
        self.assertFalse(response.data["is_active"])

    def test_open_branch_success_by_system_admin(self):
        self.branch.is_active = False
        self.branch.save()

        response = self.client.patch(
            f"/api/v1/organization/branches/{self.branch.id}/open/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.branch.refresh_from_db()
        self.assertTrue(self.branch.is_active)
        self.assertTrue(response.data["is_active"])

    def test_close_branch_by_user_with_permission(self):
        perm = Permission.objects.get(
            content_type__app_label="organization",
            codename="close_branch",
        )
        role = Role.objects.create(
            name="Branch Admin",
            organization=self.organization,
        )
        role.permissions.add(perm)

        branch_admin = User.objects.create_user(
            phone_number="+998905554433",
            password="StrongPass123",
            full_name="Branch Admin User",
            organization=self.organization,
            branch=self.branch,
            role=role,
        )
        self.client.force_authenticate(branch_admin)

        response = self.client.patch(
            f"/api/v1/organization/branches/{self.branch.id}/close/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.branch.refresh_from_db()
        self.assertFalse(self.branch.is_active)

    def test_open_branch_by_user_with_permission(self):
        self.branch.is_active = False
        self.branch.save()

        perm = Permission.objects.get(
            content_type__app_label="organization",
            codename="open_branch",
        )
        role = Role.objects.create(
            name="Branch Re-opener",
            organization=self.organization,
        )
        role.permissions.add(perm)

        branch_admin = User.objects.create_user(
            phone_number="+998905554434",
            password="StrongPass123",
            full_name="Branch Re-opener User",
            organization=self.organization,
            branch=self.branch,
            role=role,
        )
        self.client.force_authenticate(branch_admin)

        response = self.client.patch(
            f"/api/v1/organization/branches/{self.branch.id}/open/"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.branch.refresh_from_db()
        self.assertTrue(self.branch.is_active)

    def test_close_branch_forbidden_without_permission(self):
        no_perm_user = User.objects.create_user(
            phone_number="+998905554435",
            password="StrongPass123",
            full_name="No Perm User",
            organization=self.organization,
            branch=self.branch,
        )
        self.client.force_authenticate(no_perm_user)

        response = self.client.patch(
            f"/api/v1/organization/branches/{self.branch.id}/close/"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OrganizationServiceTestCase(TestCase):

    def setUp(self):
        self.country = Country.objects.create(name="O'zbekiston")
        self.region = Region.objects.create(name="Toshkent", country=self.country)
        self.district = District.objects.create(name="Chilonzor", region=self.region)

    def test_get_organization_status_counts_returns_correct_totals(self):
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

    def setUp(self):
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
