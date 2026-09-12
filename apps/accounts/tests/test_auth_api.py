from django.core.cache import cache
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User


class LoginAPITestCase(APITestCase):

    def setUp(self):
        cache.clear()
        self.role = Role.objects.create(name="Sotuvchi")
        self.user = User.objects.create_user(
            phone_number="+998901234567",
            password="StrongPass123",
            full_name="Sardor Aliyev",
            role=self.role,
        )

    def tearDown(self):
        cache.clear()

    def test_login_success(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"phone_number": "+998901234567", "password": "StrongPass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["phone_number"], "+998901234567")
        self.assertEqual(response.data["user"]["role"]["name"], "Sotuvchi")
        self.assertNotIn("password", response.data["user"])

    def test_login_wrong_password_unauthorized(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"phone_number": "+998901234567", "password": "WrongPass999"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_inactive_user_unauthorized(self):
        self.user.delete()
        response = self.client.post(
            "/api/v1/auth/login/",
            {"phone_number": "+998901234567", "password": "StrongPass123"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_password_invalid_data(self):
        response = self.client.post(
            "/api/v1/auth/login/",
            {"phone_number": "+998901234567"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenRefreshAPITestCase(APITestCase):

    def setUp(self):
        cache.clear()
        User.objects.create_user(
            phone_number="+998907654321",
            password="StrongPass123",
            full_name="Kamola Yusupova",
        )
        login = self.client.post(
            "/api/v1/auth/login/",
            {"phone_number": "+998907654321", "password": "StrongPass123"},
            format="json",
        )
        self.refresh_token = login.data["refresh"]

    def tearDown(self):
        cache.clear()

    def test_token_refresh_success(self):
        response = self.client.post(
            "/api/v1/auth/token/refresh/",
            {"refresh": self.refresh_token},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_token_refresh_invalid_token_unauthorized(self):
        response = self.client.post(
            "/api/v1/auth/token/refresh/",
            {"refresh": "invalid.token.value"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
