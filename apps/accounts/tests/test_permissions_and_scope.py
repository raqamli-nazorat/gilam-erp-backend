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
