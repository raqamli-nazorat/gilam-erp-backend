import datetime

from django.contrib.auth.models import Permission
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from apps.accounts.models import Role, User, UserBlockLog
from apps.hr.models import (
    Employee,
    EmployeeLedger,
    Position,
    RecruitmentDismissal,
    WorkSchedule,
    WorkScheduleItem,
)
from apps.hr.serializers.recruitment_dismissal import EmployeeRecruitmentSerializer
from apps.organization.models import Branch, Country, District, Organization, Region


class HRBaseAPITestCase(APITestCase):
    def setUp(self):
        self.country = Country.objects.create(name="Uzbekistan")
        self.region = Region.objects.create(name="Toshkent", country=self.country)
        self.district = District.objects.create(name="Chilonzor", region=self.region)

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
                "view_workscheduleitem",
                "add_workscheduleitem",
                "change_workscheduleitem",
                "delete_workscheduleitem",
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

    def test_employee_status_not_hired_default(self):
        emp = Employee.objects.create(
            organization=self.org1,
            branch=self.branch1,
            full_name="Hali Ishga Olinmagan",
        )
        self.client.force_authenticate(self.user_org1)
        response = self.client.get(f"/api/v1/hr/employees/{emp.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["employment_status"]["status"], "not_hired")

    def test_employee_status_active_after_recruitment(self):
        emp = Employee.objects.create(
            organization=self.org1,
            branch=self.branch1,
            full_name="Ishga Olingan",
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=emp,
            position=self.position,
            card_number="8600123456789099",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )
        self.client.force_authenticate(self.user_org1)
        response = self.client.get(f"/api/v1/hr/employees/{emp.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["employment_status"]["status"], "active")

    def test_employee_status_dismissed_after_dismissal(self):
        emp = Employee.objects.create(
            organization=self.org1,
            branch=self.branch1,
            full_name="Ishdan Chiqarilgan",
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=emp,
            position=self.position,
            card_number="8600123456789098",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.DISMISSAL,
            branch=self.branch1,
            employee=emp,
            position=self.position,
            card_number="8600123456789098",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 2, 1),
            dismissal_reason="O'z xohishiga ko'ra",
        )
        self.client.force_authenticate(self.user_org1)
        response = self.client.get(f"/api/v1/hr/employees/{emp.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["employment_status"]["status"], "dismissed")
        self.assertEqual(
            response.data["employment_status"]["reason"], "O'z xohishiga ko'ra"
        )

    def test_employee_status_active_in_one_branch_despite_dismissed_in_another(self):
        branch1b = Branch.objects.create(
            organization=self.org1,
            name="Branch 1B",
            region=self.region,
            district=self.district,
        )
        emp = Employee.objects.create(
            organization=self.org1,
            branch=self.branch1,
            full_name="Ikki Filialda Ishlagan",
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=emp,
            position=self.position,
            card_number="8600123456789001",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.DISMISSAL,
            branch=self.branch1,
            employee=emp,
            position=self.position,
            card_number="8600123456789001",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 2, 1),
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=branch1b,
            employee=emp,
            position=self.position,
            card_number="8600123456789002",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 5),
        )
        self.client.force_authenticate(self.user_org1)
        response = self.client.get(f"/api/v1/hr/employees/{emp.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["employment_status"]["status"], "active")

    def test_employee_status_active_after_same_day_dismissal_and_rehire(self):
        """Bir kunda bo'shatilib, keyin qayta ishga olingan xodim 'active' bo'lishi kerak."""
        emp = Employee.objects.create(
            organization=self.org1,
            branch=self.branch1,
            full_name="Bir Kunda Qayta Olingan",
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=emp,
            position=self.position,
            card_number="8600123456789030",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2024, 2, 14),
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.DISMISSAL,
            branch=self.branch1,
            employee=emp,
            position=self.position,
            card_number="8600123456789030",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 9, 17),
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=emp,
            position=self.position,
            card_number="8600123456789031",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 9, 17),
        )
        self.client.force_authenticate(self.user_org1)
        response = self.client.get(f"/api/v1/hr/employees/{emp.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["employment_status"]["status"], "active")

        history_response = self.client.get(
            f"/api/v1/hr/employees/{emp.id}/employment-history/"
        )
        self.assertEqual(history_response.status_code, status.HTTP_200_OK)
        self.assertTrue(history_response.data[0]["is_employed"])

    def test_employee_counts_success(self):
        active_emp = Employee.objects.create(
            organization=self.org1, branch=self.branch1, full_name="Faol Xodim"
        )
        Employee.objects.create(
            organization=self.org1, branch=self.branch1, full_name="Nofaol Xodim"
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=active_emp,
            position=self.position,
            card_number="8600123456789003",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )
        self.client.force_authenticate(self.user_org1)
        response = self.client.get("/api/v1/hr/employees/counts/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.user_org1 uchun ham avtomatik Employee yaratiladi (User.create_user
        # signali), shuning uchun bazaviy 1 ta nofaol xodim allaqachon bor.
        self.assertEqual(response.data["total"], 3)
        self.assertEqual(response.data["active"], 1)
        self.assertEqual(response.data["inactive"], 2)

    def test_employee_filter_by_is_active(self):
        active_emp = Employee.objects.create(
            organization=self.org1, branch=self.branch1, full_name="Faol Xodim"
        )
        Employee.objects.create(
            organization=self.org1, branch=self.branch1, full_name="Nofaol Xodim"
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=active_emp,
            position=self.position,
            card_number="8600123456789004",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )
        self.client.force_authenticate(self.user_org1)
        response = self.client.get("/api/v1/hr/employees/?is_active=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(ids, [str(active_emp.id)])

    def test_employee_employment_history_success(self):
        branch1b = Branch.objects.create(
            organization=self.org1,
            name="Branch 1B",
            region=self.region,
            district=self.district,
        )
        emp = Employee.objects.create(
            organization=self.org1, branch=self.branch1, full_name="Tarixli Xodim"
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=emp,
            position=self.position,
            card_number="8600123456789005",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=branch1b,
            employee=emp,
            position=self.position,
            card_number="8600123456789006",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=4000000,
            rec_dism_date=datetime.date(2021, 8, 3),
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.DISMISSAL,
            branch=branch1b,
            employee=emp,
            position=self.position,
            card_number="8600123456789006",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=4000000,
            rec_dism_date=datetime.date(2022, 1, 1),
        )
        self.client.force_authenticate(self.user_org1)
        response = self.client.get(f"/api/v1/hr/employees/{emp.id}/employment-history/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        by_branch = {row["branch"]["id"]: row for row in response.data}
        self.assertTrue(by_branch[str(self.branch1.id)]["is_employed"])
        self.assertFalse(by_branch[str(branch1b.id)]["is_employed"])
        self.assertEqual(by_branch[str(branch1b.id)]["hired_at"], "2021-08-03")

    def test_employee_filter_by_employment_status_not_hired(self):
        never_hired = Employee.objects.create(
            organization=self.org1, branch=self.branch1, full_name="Yangi Nomzod"
        )
        active_emp = Employee.objects.create(
            organization=self.org1, branch=self.branch1, full_name="Faol Xodim"
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=active_emp,
            position=self.position,
            card_number="8600123456789007",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )
        self.client.force_authenticate(self.user_org1)
        response = self.client.get("/api/v1/hr/employees/?employment_status=not_hired")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(str(never_hired.id), ids)
        self.assertNotIn(str(active_emp.id), ids)

    def test_employee_filter_by_employment_status_dismissed(self):
        dismissed_emp = Employee.objects.create(
            organization=self.org1, branch=self.branch1, full_name="Bo'shagan Xodim"
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=dismissed_emp,
            position=self.position,
            card_number="8600123456789008",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.DISMISSAL,
            branch=self.branch1,
            employee=dismissed_emp,
            position=self.position,
            card_number="8600123456789008",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 2, 1),
        )
        self.client.force_authenticate(self.user_org1)
        response = self.client.get("/api/v1/hr/employees/?employment_status=dismissed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertEqual(ids, [str(dismissed_emp.id)])

    def test_employee_filter_by_employment_status_candidates_for_recruitment(self):
        """`not_hired,dismissed` — ishga olish uchun nomzodlar ro'yxati (faol xodimlar chiqmasligi kerak)."""
        never_hired = Employee.objects.create(
            organization=self.org1, branch=self.branch1, full_name="Yangi Nomzod"
        )
        dismissed_emp = Employee.objects.create(
            organization=self.org1, branch=self.branch1, full_name="Bo'shagan Xodim"
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=dismissed_emp,
            position=self.position,
            card_number="8600123456789009",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.DISMISSAL,
            branch=self.branch1,
            employee=dismissed_emp,
            position=self.position,
            card_number="8600123456789009",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 2, 1),
        )
        active_emp = Employee.objects.create(
            organization=self.org1, branch=self.branch1, full_name="Faol Xodim"
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=active_emp,
            position=self.position,
            card_number="8600123456789010",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )
        self.client.force_authenticate(self.user_org1)
        response = self.client.get(
            "/api/v1/hr/employees/?employment_status=not_hired,dismissed"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(str(never_hired.id), ids)
        self.assertIn(str(dismissed_emp.id), ids)
        self.assertNotIn(str(active_emp.id), ids)

    def test_employee_employment_history_empty_for_new_employee(self):
        emp = Employee.objects.create(
            organization=self.org1, branch=self.branch1, full_name="Yangi Xodim"
        )
        self.client.force_authenticate(self.user_org1)
        response = self.client.get(f"/api/v1/hr/employees/{emp.id}/employment-history/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class WorkScheduleAPITestCase(HRBaseAPITestCase):
    def test_create_work_schedule_success(self):
        self.client.force_authenticate(self.user_org1)
        data = {
            "name": "Kechki smena",
            "description": "14:00-23:00, Dush-Juma",
            "branch": str(self.branch1.id),
            "from_date": "2026-01-01",
            "to_date": "2026-12-31",
            "from_hour": "14:00:00",
            "to_hour": "23:00:00",
            "work_days": [4, 0, 1, 2, 3],
        }
        response = self.client.post("/api/v1/hr/work-schedules/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["from_date"], "2026-01-01")
        self.assertEqual(response.data["work_days"], [0, 1, 2, 3, 4])
        self.assertTrue(response.data["status"])

    def test_create_work_schedule_without_dates_success(self):
        self.client.force_authenticate(self.user_org1)
        data = {
            "name": "Sanasiz grafik",
            "branch": str(self.branch1.id),
            "from_hour": "09:00:00",
            "to_hour": "18:00:00",
            "work_days": [0, 1, 2],
        }
        response = self.client.post("/api/v1/hr/work-schedules/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["from_date"])

    def test_create_work_schedule_invalid_work_days(self):
        self.client.force_authenticate(self.user_org1)
        base = {
            "name": "Kunlar",
            "branch": str(self.branch1.id),
            "from_hour": "09:00:00",
            "to_hour": "18:00:00",
        }
        cases = {
            (): "Kamida bitta ish kuni tanlanishi kerak.",
            (1, 1): "Ish kunlari takrorlanmasligi kerak.",
            (7,): "Ish kuni 0 dan 6 gacha bo'lishi kerak.",
            (18,): "Ish kuni 0 dan 6 gacha bo'lishi kerak.",
            (90,): "Ish kuni 0 dan 6 gacha bo'lishi kerak.",
        }
        for bad, message in cases.items():
            response = self.client.post(
                "/api/v1/hr/work-schedules/",
                {**base, "work_days": list(bad)},
                format="json",
            )
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, bad)
            self.assertIn(message, str(response.data["work_days"]), bad)

    def test_create_work_schedule_invalid_hours(self):
        self.client.force_authenticate(self.user_org1)
        data = {
            "name": "Noto'g'ri vaqt",
            "branch": str(self.branch1.id),
            "from_hour": "18:00:00",
            "to_hour": "09:00:00",
            "work_days": [0],
        }
        response = self.client.post("/api/v1/hr/work-schedules/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_work_schedules_by_work_day(self):
        monday = WorkSchedule.objects.create(
            branch=self.branch1,
            name="Dushanba",
            from_hour=datetime.time(9, 0),
            to_hour=datetime.time(18, 0),
            work_days=[0],
        )
        sunday = WorkSchedule.objects.create(
            branch=self.branch1,
            name="Yakshanba",
            from_hour=datetime.time(9, 0),
            to_hour=datetime.time(18, 0),
            work_days=[6],
        )
        self.client.force_authenticate(self.user_org1)
        response = self.client.get("/api/v1/hr/work-schedules/?work_day=0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(str(monday.id), ids)
        self.assertNotIn(str(sunday.id), ids)

    def test_create_work_schedule_invalid_dates(self):
        self.client.force_authenticate(self.user_org1)
        data = {
            "branch": str(self.branch1.id),
            "name": "Noto'g'ri sana",
            "from_date": "2026-12-31",
            "to_date": "2026-01-01",
            "from_hour": "09:00:00",
            "to_hour": "18:00:00",
            "work_days": [0],
        }
        response = self.client.post("/api/v1/hr/work-schedules/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_work_schedule_invalid_data(self):
        self.client.force_authenticate(self.user_org1)
        response = self.client.post("/api/v1/hr/work-schedules/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_work_schedules_unauthenticated(self):
        response = self.client.get("/api/v1/hr/work-schedules/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_work_schedules_by_is_active(self):
        active_ws = WorkSchedule.objects.create(
            branch=self.branch1,
            from_date=datetime.date(2026, 1, 1),
            to_date=datetime.date(2026, 12, 31),
            name="Asosiy smena",
            from_hour=datetime.time(9, 0),
            to_hour=datetime.time(18, 0),
        )
        inactive_ws = WorkSchedule.objects.create(
            branch=self.branch1,
            from_date=datetime.date(2026, 1, 1),
            to_date=datetime.date(2026, 12, 31),
            name="Eskirgan smena",
            from_hour=datetime.time(9, 0),
            to_hour=datetime.time(18, 0),
        )
        inactive_ws.delete()

        self.client.force_authenticate(self.user_org1)
        response = self.client.get("/api/v1/hr/work-schedules/?is_active=true")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ids = [item["id"] for item in response.data["results"]]
        self.assertIn(str(active_ws.id), ids)
        self.assertNotIn(str(inactive_ws.id), ids)

    def test_deleted_work_schedule_still_listed_as_inactive(self):
        ws = WorkSchedule.objects.create(
            branch=self.branch1,
            from_date=datetime.date(2026, 1, 1),
            to_date=datetime.date(2026, 12, 31),
            name="O'chiriladigan smena",
            from_hour=datetime.time(9, 0),
            to_hour=datetime.time(18, 0),
        )
        self.client.force_authenticate(self.user_org1)
        response = self.client.delete(f"/api/v1/hr/work-schedules/{ws.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        list_response = self.client.get("/api/v1/hr/work-schedules/")
        ids = [item["id"] for item in list_response.data["results"]]
        self.assertIn(str(ws.id), ids)
        item = next(i for i in list_response.data["results"] if i["id"] == str(ws.id))
        self.assertFalse(item["status"])


class WorkScheduleItemAPITestCase(HRBaseAPITestCase):
    def setUp(self):
        super().setUp()
        self.schedule = WorkSchedule.objects.create(
            branch=self.branch1,
            name="Asosiy smena",
            from_date=datetime.date(2026, 1, 1),
            to_date=datetime.date(2026, 12, 31),
            from_hour=datetime.time(9, 0),
            to_hour=datetime.time(18, 0),
        )

    def test_create_work_schedule_item_success(self):
        self.client.force_authenticate(self.user_org1)
        data = {
            "work_schedule": str(self.schedule.id),
            "name": "Navro'z",
            "day_type": WorkScheduleItem.DayType.FULL_HOLIDAY,
            "day_date": "2026-03-21",
            "from_hour": "00:00:00",
            "to_hour": "00:00:00",
        }
        response = self.client.post(
            "/api/v1/hr/work-schedule-items/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["day_type"], "full_holiday")

    def test_create_work_schedule_item_invalid_data(self):
        self.client.force_authenticate(self.user_org1)
        response = self.client.post(
            "/api/v1/hr/work-schedule-items/", {}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_work_schedule_items_unauthenticated(self):
        response = self.client.get("/api/v1/hr/work-schedule-items/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


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

    def test_draft_recruitment_only_affects_employee_after_approval(self):
        self.client.force_authenticate(self.user_org1)
        data = {
            "status": RecruitmentDismissal.Status.DRAFT,
            **self._recruitment_item(self.emp1, "8600123456789090"),
        }
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/", data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        record_id = response.data["id"]
        self.assertEqual(response.data["status"], RecruitmentDismissal.Status.DRAFT)
        self.assertFalse(
            EmployeeLedger.objects.filter(
                employee=self.emp1, type=EmployeeLedger.Type.RECRUITMENT
            ).exists()
        )

        response = self.client.post(
            f"/api/v1/hr/recruitment-dismissals/{record_id}/approve/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], RecruitmentDismissal.Status.APPROVED)
        self.assertTrue(
            EmployeeLedger.objects.filter(
                employee=self.emp1, type=EmployeeLedger.Type.RECRUITMENT
            ).exists()
        )

    def test_cancelled_recruitment_does_not_affect_employee(self):
        self.client.force_authenticate(self.user_org1)
        data = {
            "status": RecruitmentDismissal.Status.DRAFT,
            **self._recruitment_item(self.emp1, "8600123456789091"),
        }
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/", data, format="json"
        )
        record_id = response.data["id"]

        response = self.client.post(
            f"/api/v1/hr/recruitment-dismissals/{record_id}/cancel/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], RecruitmentDismissal.Status.CANCELLED)
        self.assertFalse(
            EmployeeLedger.objects.filter(
                employee=self.emp1, type=EmployeeLedger.Type.RECRUITMENT
            ).exists()
        )

    def test_counts_endpoint_reports_recruitment_statuses(self):
        for index, record_status in enumerate(RecruitmentDismissal.Status.values):
            RecruitmentDismissal.objects.create(
                type=RecruitmentDismissal.Type.RECRUITMENT,
                status=record_status,
                branch=self.branch1,
                employee=self.emp1,
                position=self.position,
                card_number=f"86001234567890{index}",
                salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
                fix_summa=5000000,
                rec_dism_date=datetime.date(2026, 1, 10 + index),
            )

        self.client.force_authenticate(self.admin)
        response = self.client.get("/api/v1/counts/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["recruitments"],
            {"all": 3, "draft": 1, "approved": 1, "cancelled": 1},
        )
        self.assertEqual(
            response.data["dismissals"],
            {"all": 0, "draft": 0, "approved": 0, "cancelled": 0},
        )

    def test_create_recruitment_for_already_active_employee_same_branch_invalid_data(
        self,
    ):
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=self.emp1,
            position=self.position,
            card_number="8600123456789012",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )
        self.client.force_authenticate(self.user_org1)
        data = {
            "branch": str(self.branch1.id),
            "employee": str(self.emp1.id),
            "position": str(self.position.id),
            "card_number": "8600123456789099",
            "salary_type": "fixed_amount",
            "fix_summa": "5000000.00",
            "rec_dism_date": "2026-02-01",
        }
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("employee", response.data)

    def test_create_recruitment_for_already_active_employee_other_branch_invalid_data(
        self,
    ):
        branch1b = Branch.objects.create(
            organization=self.org1,
            name="Branch 1B",
            region=self.region,
            district=self.district,
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=self.emp1,
            position=self.position,
            card_number="8600123456789012",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )
        self.client.force_authenticate(self.user_org1)
        data = {
            "branch": str(branch1b.id),
            "employee": str(self.emp1.id),
            "position": str(self.position.id),
            "card_number": "8600123456789098",
            "salary_type": "fixed_amount",
            "fix_summa": "5000000.00",
            "rec_dism_date": "2026-02-01",
        }
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("employee", response.data)

    def test_create_recruitment_for_dismissed_employee_success(self):
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=self.emp1,
            position=self.position,
            card_number="8600123456789012",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.DISMISSAL,
            branch=self.branch1,
            employee=self.emp1,
            position=self.position,
            card_number="8600123456789012",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 20),
        )
        self.client.force_authenticate(self.user_org1)
        data = {
            "branch": str(self.branch1.id),
            "employee": str(self.emp1.id),
            "position": str(self.position.id),
            "card_number": "8600123456789097",
            "salary_type": "fixed_amount",
            "fix_summa": "5000000.00",
            "rec_dism_date": "2026-02-01",
        }
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

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
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=self.emp1,
            position=self.position,
            card_number="8600123456789012",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )
        self.client.force_authenticate(self.user_org1)
        data = {
            "employee": str(self.emp1.id),
            "dismissal_reason": "O'z xohishiga ko'ra",
        }
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/dismiss/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            EmployeeLedger.objects.filter(
                employee=self.emp1,
                type=EmployeeLedger.Type.DISMISSAL_WORK,
            ).exists()
        )

    def test_bulk_create_recruitment_success(self):
        self.client.force_authenticate(self.user_org1)
        emp3 = Employee.objects.create(
            organization=self.org1,
            branch=self.branch1,
            full_name="Emp 3",
        )
        data = {
            "items": [
                {
                    "type": "recruitment",
                    "branch": str(self.branch1.id),
                    "employee": str(self.emp1.id),
                    "position": str(self.position.id),
                    "card_number": "8600123456789012",
                    "salary_type": "fixed_amount",
                    "fix_summa": "5000000.00",
                    "rec_dism_date": "2026-01-10",
                },
                {
                    "type": "recruitment",
                    "branch": str(self.branch1.id),
                    "employee": str(emp3.id),
                    "position": str(self.position.id),
                    "card_number": "8600123456789013",
                    "salary_type": "fixed_amount",
                    "fix_summa": "4500000.00",
                    "rec_dism_date": "2026-01-10",
                },
            ]
        }
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/bulk-create/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)
        self.assertTrue(
            RecruitmentDismissal.objects.filter(employee=self.emp1).exists()
        )
        self.assertTrue(RecruitmentDismissal.objects.filter(employee=emp3).exists())
        self.assertTrue(
            EmployeeLedger.objects.filter(
                employee=emp3, type=EmployeeLedger.Type.RECRUITMENT
            ).exists()
        )

    def test_bulk_create_recruitment_empty_items_invalid_data(self):
        self.client.force_authenticate(self.user_org1)
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/bulk-create/",
            {"items": []},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bulk_create_recruitment_one_invalid_item_rolls_back_all(self):
        self.client.force_authenticate(self.user_org1)
        data = {
            "items": [
                {
                    "type": "recruitment",
                    "branch": str(self.branch1.id),
                    "employee": str(self.emp1.id),
                    "position": str(self.position.id),
                    "card_number": "8600123456789012",
                    "salary_type": "fixed_amount",
                    "fix_summa": "5000000.00",
                    "rec_dism_date": "2026-01-10",
                },
                {
                    "type": "recruitment",
                    "branch": str(self.branch1.id),
                    "employee": str(self.emp2.id),
                    "position": str(self.position.id),
                    "card_number": "8600123456789013",
                    "salary_type": "fixed_amount",
                    "fix_summa": "4500000.00",
                    "rec_dism_date": "2026-01-10",
                },
            ]
        }
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/bulk-create/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            RecruitmentDismissal.objects.filter(employee=self.emp1).exists()
        )

    def _recruitment_item(self, employee, card_number):
        """Ishga olish so'rovi uchun bitta yozuv ma'lumotini qaytaradi."""
        return {
            "branch": str(self.branch1.id),
            "employee": str(employee.id),
            "position": str(self.position.id),
            "card_number": card_number,
            "salary_type": "fixed_amount",
            "fix_summa": "5000000.00",
            "rec_dism_date": "2026-01-10",
        }

    def _create_active_recruitment(self, employee):
        """Xodim uchun faol ishga olish yozuvini yaratadi."""
        return RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=employee,
            position=self.position,
            card_number="8600123456789012",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )

    def test_create_recruitment_before_last_dismissal_date_invalid_data(self):
        self._create_active_recruitment(self.emp1)
        self.client.force_authenticate(self.user_org1)
        self.client.post(
            "/api/v1/hr/recruitment-dismissals/dismiss/",
            {"employee": str(self.emp1.id), "dismissal_reason": "Ariza"},
            format="json",
        )
        item = self._recruitment_item(self.emp1, "8600123456789055")
        item["rec_dism_date"] = "2026-01-15"
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/", item, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("rec_dism_date", response.data)

    def test_bulk_dismiss_duplicate_employee_invalid_data(self):
        self._create_active_recruitment(self.emp1)
        self.client.force_authenticate(self.user_org1)
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/bulk-dismiss/",
            {"employees": [str(self.emp1.id), str(self.emp1.id)]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("employees", response.data)
        self.assertFalse(
            RecruitmentDismissal.objects.filter(
                employee=self.emp1, type=RecruitmentDismissal.Type.DISMISSAL
            ).exists()
        )

    def test_bulk_create_recruitment_duplicate_employee_invalid_data(self):
        self.client.force_authenticate(self.user_org1)
        data = {
            "items": [
                self._recruitment_item(self.emp1, "8600123456789012"),
                self._recruitment_item(self.emp1, "8600123456789013"),
            ]
        }
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/bulk-create/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            RecruitmentDismissal.objects.filter(employee=self.emp1).exists()
        )

    def test_bulk_create_recruitment_already_active_employee_invalid_data(self):
        self._create_active_recruitment(self.emp1)
        self.client.force_authenticate(self.user_org1)
        data = {"items": [self._recruitment_item(self.emp1, "8600123456789013")]}
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/bulk-create/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            RecruitmentDismissal.objects.filter(employee=self.emp1).count(), 1
        )

    def test_update_recruitment_employee_change_invalid_data(self):
        record = self._create_active_recruitment(self.emp1)
        emp3 = Employee.objects.create(
            organization=self.org1, branch=self.branch1, full_name="Emp 3"
        )
        self.client.force_authenticate(self.user_org1)
        response = self.client.patch(
            f"/api/v1/hr/recruitment-dismissals/{record.id}/",
            {"employee": str(emp3.id)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("employee", response.data)
        record.refresh_from_db()
        self.assertEqual(record.employee_id, self.emp1.id)

    def test_update_recruitment_type_change_invalid_data(self):
        self._create_active_recruitment(self.emp1)
        dismissal = RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.DISMISSAL,
            branch=self.branch1,
            employee=self.emp1,
            position=self.position,
            card_number="8600123456789012",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 20),
        )
        self.client.force_authenticate(self.user_org1)
        response = self.client.patch(
            f"/api/v1/hr/recruitment-dismissals/{dismissal.id}/",
            {"type": "recruitment"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)
        dismissal.refresh_from_db()
        self.assertEqual(dismissal.type, RecruitmentDismissal.Type.DISMISSAL)

    def test_create_recruitment_concurrent_active_record_invalid_data(self):
        """Tekshiruvdan keyin, saqlashdan oldin boshqa so'rov xodimni ishga olsa — saqlanmaydi."""
        serializer = EmployeeRecruitmentSerializer(
            data=self._recruitment_item(self.emp1, "8600123456789012")
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self._create_active_recruitment(self.emp1)
        with self.assertRaises(ValidationError):
            serializer.save()
        self.assertEqual(
            RecruitmentDismissal.objects.filter(employee=self.emp1).count(), 1
        )

    def test_bulk_create_recruitment_unauthenticated(self):
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/bulk-create/",
            {"items": []},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

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

    def test_dismissal_blocks_linked_user_account(self):
        linked_user = User.objects.create_user(
            phone_number="+998904444444",
            password="StrongPassword123",
            full_name="Linked User",
            employee=self.emp1,
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=self.emp1,
            position=self.position,
            card_number="8600123456789020",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )
        self.client.force_authenticate(self.user_org1)
        data = {
            "employee": str(self.emp1.id),
            "dismissal_reason": "Xodim ishdan bo'shadi",
        }
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/dismiss/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        block_log = UserBlockLog.objects.filter(
            user=linked_user, type=UserBlockLog.Type.BLOCK
        ).first()
        self.assertIsNotNone(block_log)
        self.assertEqual(block_log.reason, "Xodim ishdan bo'shadi")
        self.assertEqual(block_log.actor, self.user_org1)

    def test_recruitment_unblocks_linked_user_account(self):
        linked_user = User.objects.create_user(
            phone_number="+998905555555",
            password="StrongPassword123",
            full_name="Linked User 2",
            employee=self.emp1,
        )
        UserBlockLog.objects.create(
            user=linked_user, type=UserBlockLog.Type.BLOCK, reason="Avvalgi sabab"
        )
        self.client.force_authenticate(self.user_org1)
        data = {
            "type": "recruitment",
            "branch": str(self.branch1.id),
            "employee": str(self.emp1.id),
            "position": str(self.position.id),
            "card_number": "8600123456789021",
            "salary_type": "fixed_amount",
            "fix_summa": "5000000.00",
            "rec_dism_date": "2026-03-01",
        }
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            UserBlockLog.objects.filter(
                user=linked_user, type=UserBlockLog.Type.UNBLOCK
            ).exists()
        )

    def test_dismissal_without_linked_user_does_not_fail(self):
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=self.branch1,
            employee=self.emp1,
            position=self.position,
            card_number="8600123456789022",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
        )
        self.client.force_authenticate(self.user_org1)
        data = {
            "employee": str(self.emp1.id),
            "dismissal_reason": "Sabab",
        }
        response = self.client.post(
            "/api/v1/hr/recruitment-dismissals/dismiss/", data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(UserBlockLog.objects.exists())


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
        response = self.client.post("/api/v1/hr/employee-ledgers/", data, format="json")
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
