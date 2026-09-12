from django.contrib.auth.models import Permission
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User
from apps.organization.models import Branch, Country, District, Organization, Region


class PermissionAndScopeTestCase(APITestCase):

    def setUp(self):
        self.country = Country.objects.create(name="Uzbekistan")
        self.region = Region.objects.create(name="Toshkent", country=self.country)
        self.district = District.objects.create(name="Chilonzor", region=self.region)

        self.org1 = Organization.objects.create(
            name="Org 1", inn="111111111", region=self.region, district=self.district
        )
        self.org2 = Organization.objects.create(
            name="Org 2", inn="222222222", region=self.region, district=self.district
        )

        self.b1 = Branch.objects.create(
            name="Org1 Branch 1",
            organization=self.org1,
            region=self.region,
            district=self.district,
        )
        self.b2 = Branch.objects.create(
            name="Org1 Branch 2",
            organization=self.org1,
            region=self.region,
            district=self.district,
        )
        self.b3 = Branch.objects.create(
            name="Org1 Branch 3",
            organization=self.org1,
            region=self.region,
            district=self.district,
        )
        self.b_other = Branch.objects.create(
            name="Org2 Branch",
            organization=self.org2,
            region=self.region,
            district=self.district,
        )

        self.system_role = Role.objects.create(
            name="Platform Super Admin", organization=None, is_system=True
        )
        self.org1_role = Role.objects.create(
            name="Org 1 Operator", organization=self.org1
        )
        self.org2_role = Role.objects.create(
            name="Org 2 Operator", organization=self.org2
        )

    def test_user_without_permission_cannot_view(self):
        user = User.objects.create_user(
            phone_number="+998901110001",
            password="Password123",
            full_name="No Perm User",
            organization=self.org1,
            role=self.org1_role,
        )
        self.client.force_authenticate(user)
        response = self.client.get("/api/v1/accounts/roles/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_with_view_permission_can_list_but_cannot_create(self):
        view_perm = Permission.objects.get(
            content_type__app_label="accounts", codename="view_role"
        )
        self.org1_role.permissions.add(view_perm)

        user = User.objects.create_user(
            phone_number="+998901110002",
            password="Password123",
            full_name="View Only User",
            organization=self.org1,
            role=self.org1_role,
        )
        self.client.force_authenticate(user)

        list_resp = self.client.get("/api/v1/accounts/roles/")
        self.assertEqual(list_resp.status_code, status.HTTP_200_OK)

        create_resp = self.client.post(
            "/api/v1/accounts/roles/", {"name": "New Role Attempt"}, format="json"
        )
        self.assertEqual(create_resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_with_add_permission_can_create_role(self):
        view_perm = Permission.objects.get(
            content_type__app_label="accounts", codename="view_role"
        )
        add_perm = Permission.objects.get(
            content_type__app_label="accounts", codename="add_role"
        )
        self.org1_role.permissions.add(view_perm, add_perm)

        user = User.objects.create_user(
            phone_number="+998901110003",
            password="Password123",
            full_name="Manager User",
            organization=self.org1,
            role=self.org1_role,
        )
        self.client.force_authenticate(user)

        response = self.client.post(
            "/api/v1/accounts/roles/", {"name": "Sotuv Boshlig'i"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_role = Role.objects.get(name="Sotuv Boshlig'i")
        self.assertEqual(created_role.organization_id, self.org1.id)
        self.assertFalse(created_role.is_system)

    def test_system_and_other_org_roles_hidden_from_tenant_user(self):
        view_perm = Permission.objects.get(
            content_type__app_label="accounts", codename="view_role"
        )
        self.org1_role.permissions.add(view_perm)

        user = User.objects.create_user(
            phone_number="+998901110004",
            password="Password123",
            full_name="Org1 Admin",
            organization=self.org1,
            role=self.org1_role,
        )
        self.client.force_authenticate(user)

        response = self.client.get("/api/v1/accounts/roles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = {item["id"] for item in response.data["results"]}
        self.assertIn(str(self.org1_role.id), returned_ids)
        self.assertNotIn(str(self.system_role.id), returned_ids)
        self.assertNotIn(str(self.org2_role.id), returned_ids)

    def test_branch_scoping_in_branch_list(self):
        view_branch_perm = Permission.objects.get(
            content_type__app_label="organization", codename="view_branch"
        )
        self.org1_role.permissions.add(view_branch_perm)

        self.org1_role.branches.set([self.b1])

        user = User.objects.create_user(
            phone_number="+998901110005",
            password="Password123",
            full_name="Branch 1 User",
            organization=self.org1,
            role=self.org1_role,
        )
        self.client.force_authenticate(user)

        response = self.client.get("/api/v1/organization/branches/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = {item["id"] for item in response.data["results"]}
        self.assertIn(str(self.b1.id), returned_ids)
        self.assertNotIn(str(self.b2.id), returned_ids)
        self.assertNotIn(str(self.b3.id), returned_ids)
        self.assertNotIn(str(self.b_other.id), returned_ids)

    def test_combined_branches_scoping(self):
        view_branch_perm = Permission.objects.get(
            content_type__app_label="organization", codename="view_branch"
        )
        self.org1_role.permissions.add(view_branch_perm)

        self.org1_role.branches.set([self.b1, self.b2])

        user = User.objects.create_user(
            phone_number="+998901110006",
            password="Password123",
            full_name="Multi Branch User",
            organization=self.org1,
            role=self.org1_role,
            branch=self.b3,
        )
        self.client.force_authenticate(user)

        response = self.client.get("/api/v1/organization/branches/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = {item["id"] for item in response.data["results"]}
        self.assertIn(str(self.b1.id), returned_ids)
        self.assertIn(str(self.b2.id), returned_ids)
        self.assertIn(str(self.b3.id), returned_ids)
        self.assertNotIn(str(self.b_other.id), returned_ids)

    def test_authenticated_user_can_view_regions_and_districts_without_permission(self):
        user = User.objects.create_user(
            phone_number="+998901110007",
            password="Password123",
            full_name="Ordinary Employee",
            organization=self.org1,
            role=self.org1_role,
        )
        self.client.force_authenticate(user)

        resp_country = self.client.get("/api/v1/organization/countries/")
        self.assertEqual(resp_country.status_code, status.HTTP_200_OK)

        resp_region = self.client.get("/api/v1/organization/regions/")
        self.assertEqual(resp_region.status_code, status.HTTP_200_OK)

        resp_district = self.client.get("/api/v1/organization/districts/")
        self.assertEqual(resp_district.status_code, status.HTTP_200_OK)

        resp_create = self.client.post(
            "/api/v1/organization/regions/",
            {"name": "Buxoro", "country": str(self.country.id)},
            format="json",
        )
        self.assertEqual(resp_create.status_code, status.HTTP_403_FORBIDDEN)

    def test_system_permissions_hidden_from_tenant_permissions_endpoint(self):
        view_perm = Permission.objects.get(
            content_type__app_label="auth", codename="view_permission"
        )
        self.org1_role.permissions.add(view_perm)

        user = User.objects.create_user(
            phone_number="+998901110008",
            password="Password123",
            full_name="Tenant Admin",
            organization=self.org1,
            role=self.org1_role,
        )
        self.client.force_authenticate(user)

        response = self.client.get("/api/v1/accounts/permissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


        all_codenames = []
        for model_group, perms in response.data.items():
            for p in perms:
                all_codenames.append(p["codename"])

        forbidden_system_codenames = [
            "add_organization",
            "delete_organization",
            "suspend_organization",
            "activate_organization",
            "add_country",
            "change_country",
            "delete_country",
            "add_region",
            "change_region",
            "delete_region",
            "add_district",
            "change_district",
            "delete_district",
        ]
        for f_code in forbidden_system_codenames:
            self.assertNotIn(f_code, all_codenames)

    def test_tenant_cannot_create_role_with_country_or_region_add_perm(self):
        add_role_perm = Permission.objects.get(
            content_type__app_label="accounts", codename="add_role"
        )
        self.org1_role.permissions.add(add_role_perm)

        user = User.objects.create_user(
            phone_number="+998901110009",
            password="Password123",
            full_name="Tenant Admin 2",
            organization=self.org1,
            role=self.org1_role,
        )
        self.client.force_authenticate(user)

        add_country_perm = Permission.objects.get(
            content_type__app_label="organization", codename="add_country"
        )
        response = self.client.post(
            "/api/v1/accounts/roles/",
            {
                "name": "Hacker Role",
                "permissions": [add_country_perm.id],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_tenant_cannot_create_role_with_suspend_organization_perm(self):
        add_role_perm = Permission.objects.get(
            content_type__app_label="accounts", codename="add_role"
        )
        self.org1_role.permissions.add(add_role_perm)

        user = User.objects.create_user(
            phone_number="+998901110010",
            password="Password123",
            full_name="Tenant Admin 3",
            organization=self.org1,
            role=self.org1_role,
        )
        self.client.force_authenticate(user)

        suspend_perm = Permission.objects.get(
            content_type__app_label="organization", codename="suspend_organization"
        )
        response = self.client.post(
            "/api/v1/accounts/roles/",
            {
                "name": "Suspend Role",
                "permissions": [suspend_perm.id],
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

