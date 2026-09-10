"""
Accounts app CRUD endpointlari uchun API testlari.

`UserSerializer` da parolni hash qilish va yangilash mantig'i alohida tekshiriladi.
"""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User


class RoleAPITestCase(APITestCase):
    """Role endpointlari testi."""

    def setUp(self):
        """Superuser tayyorlaydi va autentifikatsiya qiladi."""
        self.user = User.objects.create_superuser(
            phone_number="+998900000001",
            password="StrongPass123",
            full_name="Admin",
        )
        self.client.force_authenticate(self.user)

    def test_create_role_success(self):
        """POST /roles/ — 201."""
        response = self.client.post(
            "/api/v1/accounts/roles/", {"name": "Sotuvchi"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Role.objects.filter(name="Sotuvchi").exists())

    def test_list_roles_success(self):
        """GET /roles/ — 200."""
        Role.objects.create(name="Kassir")
        response = self.client.get("/api/v1/accounts/roles/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_list_unauthenticated(self):
        """Autentifikatsiyasiz so'rov — 401."""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/accounts/roles/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserAPITestCase(APITestCase):
    """User endpointlari va parol mantig'i testi."""

    def setUp(self):
        """Superuser va rol tayyorlaydi."""
        self.admin = User.objects.create_superuser(
            phone_number="+998900000002",
            password="StrongPass123",
            full_name="Admin",
        )
        self.client.force_authenticate(self.admin)
        self.role = Role.objects.create(name="Sotuvchi")

    def test_create_user_hashes_password(self):
        """POST /users/ — 201, parol javobda ko'rinmaydi va hash qilinadi."""
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
        """POST /users/ — qisqa parol (min 8) bo'lsa 400."""
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
        """PATCH /users/{id}/ — yangi parol berilsa qayta hash qilinadi."""
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
        """PATCH /users/{id}/ — parolsiz yangilash mumkin (200)."""
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
        """Autentifikatsiyasiz so'rov — 401."""
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/accounts/users/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
