import datetime
from django.contrib.auth.models import Permission
from rest_framework import status
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User
from apps.hr.models import (
    Employee,
    EmployeeLedger,
    Position,
    RecruitmentDismissal,
    WorkSchedule,
    WorkScheduleItem,
)
from apps.organization.models import Branch, Country, District, Organization, Region


class HRBaseAPITestCase(APITestCase):

    def setUp(self):
        self.country = Country.objects.create(name="Uzbekistan")
        self.region = Region.objects.create(
            name="Toshkent", country=self.country
        )
        self.district = District.objects.create(
            name="Chilonzor", region=self.region
        )

        self.org1 = Organization.objects.create(
            name="Org 1",
            region=self.region,
            district=self.district,
            inn="111111111",
        )
        self.branch1 = Branch.objects.create(
            organization=self.org1,
            name="Branch 1",
            region=self.region,
            district=self.district,
        )

        self.org2 = Organization.objects.create(
            name="Org 2",
            region=self.region,
            district=self.district,
            inn="222222222",
        )
        self.branch2 = Branch.objects.create(
            organization=self.org2,
            name="Branch 2",
            region=self.region,
            district=self.district,
        )

        self.admin = User.objects.create_superuser(
            phone_number="+998901110001",
            password="StrongPassword123",
            full_name="System Admin",
        )

        self.role_org1 = Role.objects.create(
            name="Org 1 HR Manager",
            organization=self.org1,
        )
        hr_perms = Permission.objects.filter(
            content_type__app_label="hr",
            codename__in=[
                "view_employee",
                "add_employee",
                "change_employee",
                "delete_employee",
                "view_workschedule",
                "add_workschedule",
                "change_workschedule",
                "delete_workschedule",
                "view_recruitmentdismissal",
                "add_recruitmentdismissal",
                "change_recruitmentdismissal",
                "delete_recruitmentdismissal",
                "view_employeeledger",
                "add_employeeledger",
                "change_employeeledger",
                "delete_employeeledger",
                "view_position",
            ],
        )
        self.role_org1.permissions.set(hr_perms)

        self.user_org1 = User.objects.create_user(
            phone_number="+998901110002",
            password="StrongPassword123",
            full_name="Org 1 HR",
            organization=self.org1,
            role=self.role_org1,
        )

        self.user_org2 = User.objects.create_user(
            phone_number="+998901110003",
            password="StrongPassword123",
            full_name="Org 2 User",
            organization=self.org2,
        )

        self.position = Position.objects.create(name="Dasturchi")


class PositionAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_superuser(
            phone_number="+998901112233",
            password="StrongPass123",
            full_name="Test Admin",
        )
        self.client.force_authenticate(self.user)
        self.position = Position.objects.create(name="Direktor")

    def test_list_positions_success(self):
        response = self.client.get("/api/v1/hr/positions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_create_position_success(self):
        response = self.client.post(
            "/api/v1/hr/positions/",
            {"name": "Sotuvchi", "description": "Savdo maslahatchisi"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Position.objects.filter(name="Sotuvchi").exists())

    def test_create_position_invalid_data(self):
        response = self.client.post("/api/v1/hr/positions/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_position_soft_delete(self):
        response = self.client.delete(f"/api/v1/hr/positions/{self.position.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.position.refresh_from_db()
        self.assertFalse(self.position.is_active)
        list_response = self.client.get("/api/v1/hr/positions/")
        self.assertEqual(list_response.data["count"], 0)

    def test_list_positions_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/v1/hr/positions/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class EmployeeAPITestCase(HRBaseAPITestCase):

    def test_create_employee_as_org_user(self):
        self.client.force_authenticate(self.user_org1)
        response = self.client.post(
            "/api/v1/hr/employees/",
            {
                "full_name": "Ali Valiyev",
                "phone_number": "+998901234567",
                "branch": str(self.branch1.id),
                "region": str(self.region.id),
                "district": str(self.district.id),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        employee = Employee.objects.get(id=response.data["id"])
        self.assertEqual(employee.organization, self.org1)
        self.assertEqual(employee.branch, self.branch1)

    def test_create_employee_branch_from_other_org_fails(self):
        self.client.force_authenticate(self.user_org1)
        response = self.client.post(
            "/api/v1/hr/employees/",
            {
                "full_name": "Vali Aliyev",
                "branch": str(self.branch2.id),
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_employee_scoping_per_organization(self):
        emp1 = Employee.objects.create(
            organization=self.org1,
            branch=self.branch1,
            full_name="Employee 1 Org 1",
        )
        emp2 = Employee.objects.create(
            organization=self.org2,
            branch=self.branch2,
            full_name="Employee 2 Org 2",
        )

        self.client.force_authenticate(self.user_org1)
        response = self.client.get("/api/v1/hr/employees/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(str(emp1.id), ids)
        self.assertNotIn(str(emp2.id), ids)

        self.client.force_authenticate(self.admin)
        admin_response = self.client.get("/api/v1/hr/employees/")
        self.assertEqual(admin_response.status_code, status.HTTP_200_OK)
        admin_ids = [item["id"] for item in admin_response.data["results"]]
        self.assertIn(str(emp1.id), admin_ids)
        self.assertIn(str(emp2.id), admin_ids)

    def test_employee_soft_delete(self):
        emp = Employee.objects.create(
            organization=self.org1,
            branch=self.branch1,
            full_name="ToDelete",
        )
        self.client.force_authenticate(self.user_org1)
        response = self.client.delete(f"/api/v1/hr/employees/{emp.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        emp.refresh_from_db()
        self.assertFalse(emp.is_active)

    def test_employee_permission_denied_without_perm(self):
        self.client.force_authenticate(self.user_org2)
        response = self.client.get("/api/v1/hr/employees/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class WorkScheduleAPITestCase(HRBaseAPITestCase):

    def test_create_work_schedule_with_items(self):
        self.client.force_authenticate(self.user_org1)
        data = {
            "branch": str(self.branch1.id),
            "name": "2026 Q1 Schedule",
            "from_date": "2026-01-01",
            "to_date": "2026-03-31",
            "from_hour": "09:00:00",
            "to_hour": "18:00:00",
            "items": [
                {
                    "name": "Ish kuni",
                    "day_type": "full_workday",
                    "day_date": "2026-01-02",
                    "from_hour": "09:00:00",
                    "to_hour": "18:00:00",
                },
                {
                    "name": "Yangi yil bayrami",
                    "day_type": "full_holiday",
                    "day_date": "2026-01-01",
                    "from_hour": "00:00:00",
                    "to_hour": "00:00:00",
                },
            ],
        }
        response = self.client.post("/api/v1/hr/work-schedules/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        schedule_id = response.data["id"]
        schedule = WorkSchedule.objects.get(id=schedule_id)
        self.assertEqual(schedule.items.count(), 2)

    def test_work_schedule_scoping(self):
        ws1 = WorkSchedule.objects.create(
            branch=self.branch1,
            name="Org 1 Schedule",
            from_date=datetime.date(2026, 1, 1),
            to_date=datetime.date(2026, 1, 31),
            from_hour=datetime.time(9, 0),
            to_hour=datetime.time(18, 0),
        )
        ws2 = WorkSchedule.objects.create(
            branch=self.branch2,
            name="Org 2 Schedule",
            from_date=datetime.date(2026, 1, 1),
            to_date=datetime.date(2026, 1, 31),
            from_hour=datetime.time(9, 0),
            to_hour=datetime.time(18, 0),
        )

        self.client.force_authenticate(self.user_org1)
        response = self.client.get("/api/v1/hr/work-schedules/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(str(ws1.id), ids)
        self.assertNotIn(str(ws2.id), ids)


class RecruitmentDismissalAPITestCase(HRBaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.emp1 = Employee.objects.create(
            organization=self.org1,
            branch=self.branch1,
            full_name="Emp 1",
        )
        self.emp2 = Employee.objects.create(
            organization=self.org2,
            branch=self.branch2,
            full_name="Emp 2",
        )

    def test_create_recruitment_success(self):
        self.client.force_authenticate(self.user_org1)
        data = {
            "type": "recruitment",
            "branch": str(self.branch1.id),
            "employee": str(self.emp1.id),
            "position": str(self.position.id),
            "card_number": "8600123456789012",
            "salary_type": "fixed_amount",
            "fix_summa": "5000000.00",
            "rec_dism_date": "2026-01-10",
        }
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            RecruitmentDismissal.objects.filter(employee=self.emp1).exists()
        )
        self.assertTrue(
            EmployeeLedger.objects.filter(
                employee=self.emp1, type=EmployeeLedger.Type.RECRUITMENT
            ).exists()
        )

    def test_position_change_triggers_employee_ledger(self):
        self.client.force_authenticate(self.user_org1)
        rec = RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=self.emp1,
            position=self.position,
            card_number="8600123456789012",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )
        new_position = Position.objects.create(name="Yetakchi Dasturchi")
        response = self.client.patch(
            f"/api/v1/hr/recruitment-dismissals/{rec.id}/",
            {"position": str(new_position.id)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(
            EmployeeLedger.objects.filter(
                employee=self.emp1,
                type=EmployeeLedger.Type.CHANGE_POSITION,
            ).exists()
        )

    def test_dismissal_triggers_employee_ledger(self):
        self.client.force_authenticate(self.user_org1)
        data = {
            "type": "dismissal",
            "branch": str(self.branch1.id),
            "employee": str(self.emp1.id),
            "position": str(self.position.id),
            "card_number": "8600123456789012",
            "salary_type": "fixed_amount",
            "fix_summa": "5000000.00",
            "rec_dism_date": "2026-02-01",
            "dismissal_reason": "O'z xohishiga ko'ra",
        }
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            EmployeeLedger.objects.filter(
                employee=self.emp1,
                type=EmployeeLedger.Type.DISMISSAL_WORK,
            ).exists()
        )

    def test_create_recruitment_with_other_org_employee_fails(self):
        self.client.force_authenticate(self.user_org1)
        data = {
            "type": "recruitment",
            "branch": str(self.branch1.id),
            "employee": str(self.emp2.id),
            "position": str(self.position.id),
            "card_number": "8600123456789012",
            "salary_type": "fixed_amount",
            "fix_summa": "5000000.00",
            "rec_dism_date": "2026-01-10",
        }
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EmployeeLedgerAPITestCase(HRBaseAPITestCase):

    def setUp(self):
        super().setUp()
        self.emp1 = Employee.objects.create(
            organization=self.org1,
            branch=self.branch1,
            full_name="Emp 1",
        )

    def test_employee_ledger_read_only_post_disallowed(self):
        self.client.force_authenticate(self.user_org1)
        data = {
            "branch": str(self.branch1.id),
            "employee": str(self.emp1.id),
            "type": "recruitment",
        }
        response = self.client.post(
            "/api/v1/hr/employee-ledgers/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_list_employee_ledgers_scoped(self):
        EmployeeLedger.objects.create(
            branch=self.branch1,
            employee=self.emp1,
            type=EmployeeLedger.Type.RECRUITMENT,
        )
        emp_other = Employee.objects.create(
            organization=self.org2,
            branch=self.branch2,
            full_name="Emp Other",
        )
        EmployeeLedger.objects.create(
            branch=self.branch2,
            employee=emp_other,
            type=EmployeeLedger.Type.RECRUITMENT,
        )

        self.client.force_authenticate(self.user_org1)
        response = self.client.get("/api/v1/hr/employee-ledgers/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["employee_info"]["id"], str(self.emp1.id)
        )
