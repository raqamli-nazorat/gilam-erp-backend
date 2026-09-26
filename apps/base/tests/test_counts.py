from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import User, UserBlockLog
from apps.organization.models import (
    Branch,
    Country,
    District,
    Organization,
    Region,
)


class CountsAPITestCase(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            phone_number="+998900000001",
            password="StrongPassword123",
            full_name="System Admin",
        )
        self.client.force_authenticate(self.admin)

        country = Country.objects.create(name="Uzbekistan")
        region = Region.objects.create(name="Toshkent", country=country)
        district = District.objects.create(name="Chilonzor", region=region)
        self.org_active = Organization.objects.create(
            name="Faol tashkilot", inn="100000001", region=region, district=district
        )
        self.org_suspended = Organization.objects.create(
            name="To'xtatilgan tashkilot",
            inn="100000002",
            region=region,
            district=district,
            is_suspended=True,
        )
        self.branch_open = Branch.objects.create(
            organization=self.org_active,
            name="Ochiq filial",
            region=region,
            district=district,
        )
        self.branch_closed = Branch.objects.create(
            organization=self.org_active,
            name="Yopiq filial",
            region=region,
            district=district,
            is_closed=True,
        )

        self.active_user = User.objects.create_user(
            phone_number="+998900000002",
            password="StrongPassword123",
            full_name="Faol user",
            organization=self.org_active,
            branch=self.branch_open,
        )
        self.blocked_user = User.objects.create_user(
            phone_number="+998900000003",
            password="StrongPassword123",
            full_name="Bloklangan user",
            organization=self.org_active,
            branch=self.branch_open,
        )
        UserBlockLog.objects.create(
            user=self.blocked_user, type=UserBlockLog.Type.BLOCK, actor=self.admin
        )

    def test_model_count_actions_return_their_status_summaries(self):
        responses = {
            "organizations": self.client.get(
                "/api/v1/organization/organizations/count/"
            ),
            "branches": self.client.get("/api/v1/organization/branches/count/"),
            "users": self.client.get("/api/v1/accounts/users/count/"),
        }

        for response in responses.values():
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            responses["organizations"].data,
            {"active": 1, "suspended": 1},
        )
        self.assertEqual(
            responses["branches"].data,
            {"active": 1, "closed": 1},
        )
        self.assertEqual(
            responses["users"].data,
            {"all": 3, "active": 2, "blocked": 1},
        )
        self.assertEqual(
            self.client.get("/api/v1/counts/").status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_counts_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.get("/api/v1/organization/organizations/count/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
