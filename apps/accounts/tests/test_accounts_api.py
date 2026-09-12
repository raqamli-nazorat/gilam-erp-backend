from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User


class RoleAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            phone_number="+998900000001",
            password="StrongPass123",
            full_name="Admin",
        )
        self.client.force_authenticate(self.user)

    def test_create_role_success(self):
        response = self.client.post(
            "/api/v1/accounts/roles/", {"name": "Sotuvchi"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Role.objects.filter(name="Sotuvchi").exists())

    def test_list_roles_success(self):
        Role.objects.create(name="Kassir")
        response = self.client.get("/api/v1/accounts/roles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_list_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/accounts/roles/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PermissionAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            phone_number="+998900000099",
            password="StrongPass123",
            full_name="Admin",
        )
        self.client.force_authenticate(self.user)

    def test_list_permissions_grouped(self):
        response = self.client.get("/api/v1/accounts/permissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)

        self.assertTrue(len(response.data.keys()) > 0)


class UserAPITestCase(APITestCase):

    def setUp(self):
        self.admin = User.objects.create_superuser(
            phone_number="+998900000002",
            password="StrongPass123",
            full_name="Admin",
        )
        self.client.force_authenticate(self.admin)
        self.role = Role.objects.create(name="Sotuvchi")

    def test_create_user_hashes_password(self):
        response = self.client.post(
            "/api/v1/accounts/users/",
            {
                "full_name": "Yangi Xodim",
                "phone_number": "+998911234567",
                "password": "SecretPass123",
                "role": str(self.role.id),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)

        created = User.objects.get(phone_number="+998911234567")
        self.assertNotEqual(created.password, "SecretPass123")
        self.assertTrue(created.check_password("SecretPass123"))

    def test_create_user_invalid_data(self):
        response = self.client.post(
            "/api/v1/accounts/users/",
            {
                "full_name": "Xodim",
                "phone_number": "+998911111111",
                "password": "123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_user_changes_password(self):
        target = User.objects.create_user(
            phone_number="+998911222333",
            password="OldPass123",
            full_name="Eski Xodim",
        )
        response = self.client.patch(
            f"/api/v1/accounts/users/{target.id}/",
            {"password": "BrandNew123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        self.assertTrue(target.check_password("BrandNew123"))

    def test_update_user_without_password_success(self):
        target = User.objects.create_user(
            phone_number="+998911444555",
            password="OldPass123",
            full_name="Xodim",
        )
        response = self.client.patch(
            f"/api/v1/accounts/users/{target.id}/",
            {"full_name": "Yangilangan Ism"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        target.refresh_from_db()
        self.assertEqual(target.full_name, "Yangilangan Ism")
        self.assertTrue(target.check_password("OldPass123"))

    def test_list_users_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_accessible_branches_combines_role_and_user_branch(self):
        from apps.organization.models import Branch, Country, District, Organization, Region

        country = Country.objects.create(name="Uzbekistan")
        region = Region.objects.create(name="Toshkent", country=country)
        district = District.objects.create(name="Chilonzor", region=region)

        org = Organization.objects.create(
            name="Test Org",
            inn="999888777",
            region=region,
            district=district,
        )
        b1 = Branch.objects.create(
            name="Branch 1", organization=org, region=region, district=district
        )
        b2 = Branch.objects.create(
            name="Branch 2", organization=org, region=region, district=district
        )
        b3 = Branch.objects.create(
            name="Branch 3", organization=org, region=region, district=district
        )

        role = Role.objects.create(name="Multi Branch Role", organization=org)
        role.branches.set([b1, b2])

        user = User.objects.create_user(
            phone_number="+998909998877",
            password="Password123",
            full_name="Branch User",
            organization=org,
            role=role,
            branch=b3,
        )

        accessible = set(user.get_accessible_branches().values_list("id", flat=True))
        self.assertEqual(accessible, {b1.id, b2.id, b3.id})


