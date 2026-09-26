import datetime
from decimal import Decimal

from django.contrib.auth.models import Permission
from rest_framework import status
from rest_framework.exceptions import ValidationError

from apps.finance.models import (
    AccrualRetention,
    AccrualRetentionDocument,
    Currency,
    CurrencyLedger,
)
from apps.hr.models import (
    CalculatingSalary,
    Employee,
    EmployeeTimesheet,
    EmployeeTimesheetItem,
    RecruitmentDismissal,
)
from apps.hr.services.salary import approve_salary, calculate_salaries, cancel_salary

from .test_hr_api import HRBaseAPITestCase

SALARIES_URL = "/api/v1/hr/calculating-salaries/"
TZ = datetime.timezone(datetime.timedelta(hours=5))


def at(day, hour=0):
    """2026-yil yanvaridagi kun uchun aware datetime."""
    return datetime.datetime(2026, 1, day, hour, tzinfo=TZ)


class SalaryBaseTestCase(HRBaseAPITestCase):
    def setUp(self):
        super().setUp()
        perms = Permission.objects.filter(
            content_type__app_label="hr",
            codename__in=[
                f"{action}_calculatingsalary"
                for action in ("view", "add", "change", "delete")
            ],
        )
        self.role_org1.permissions.add(*perms)
        self.uzs = Currency.objects.create(name="So'm", short_name="UZS")
        self.usd = Currency.objects.create(name="Dollar", short_name="USD")
        CurrencyLedger.objects.create(currency=self.usd, day=at(15).date(), value=12500)
        self.employee = self.hire("Xodim 1")
        self.client.force_authenticate(self.user_org1)

    def hire(self, full_name, branch=None, org=None, **record_kwargs):
        """Ishlab turgan xodim yaratadi (standart: belgilangan summa 5 000 000)."""
        branch = branch or self.branch1
        employee = Employee.objects.create(
            organization=org or self.org1, branch=branch, full_name=full_name
        )
        values = {
            "type": RecruitmentDismissal.Type.RECRUITMENT,
            "branch": branch,
            "employee": employee,
            "position": self.position,
            "card_number": "8600123456789012",
            "salary_type": RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            "fix_summa": 5000000,
            "rec_dism_date": datetime.date(2025, 12, 1),
        }
        values.update(record_kwargs)
        RecruitmentDismissal.objects.create(**values)
        return employee

    def approved_timesheet(self, branch=None):
        """Yanvar oyi uchun tasdiqlangan tabel."""
        return EmployeeTimesheet.objects.create(
            branch=branch or self.branch1,
            for_month=1,
            status=EmployeeTimesheet.Status.APPROVED,
        )

    def add_hours(self, timesheet, employee, plan_fact_by_day):
        """Tabelga {kun: (reja, fakt)} qatorlarini qo'shadi."""
        for day, (plan, fact) in plan_fact_by_day.items():
            EmployeeTimesheetItem.objects.create(
                employee_timesheet=timesheet,
                employee=employee,
                date=at(day),
                work_hour_in_plan=plan,
                work_hour_in_fact=fact,
            )

    def add_document(self, accrual, employee=None, day=20):
        """Tasdiqlangan hisoblash / ushlab qolish hujjati."""
        return AccrualRetentionDocument.objects.create(
            branch=self.branch1,
            employee=employee or self.employee,
            accrual_retention=accrual,
            date=at(day, 10),
            status=AccrualRetentionDocument.Status.APPROVED,
        )

    def accrual(self, **kwargs):
        """Ma'lumotnoma yozuvi yaratadi."""
        return AccrualRetention.objects.create(**kwargs)

    def salary(self, **overrides):
        """Qoralama oylik qatorini bazada yaratadi."""
        values = {
            "branch": self.branch1,
            "employee": self.employee,
            "for_month": 1,
            "amount": 4000000,
            "currency": self.uzs,
            "currency_amount": 4000000,
        }
        values.update(overrides)
        return CalculatingSalary.objects.create(**values)

    def calculate(self, **overrides):
        """`calculate/` endpointini chaqiradi."""
        data = {"branch": str(self.branch1.id), "for_month": 1, "year": 2026}
        data.update(overrides)
        return self.client.post(f"{SALARIES_URL}calculate/", data, format="json")


class CalculatingSalaryCrudTestCase(SalaryBaseTestCase):
    def salary_data(self, **overrides):
        """Standart to'g'ri oylik ma'lumotlari."""
        data = {
            "branch": str(self.branch1.id),
            "employee": str(self.employee.id),
            "for_month": 1,
            "amount": "4000000.00",
            "currency": str(self.uzs.id),
            "currency_amount": "4000000.00",
        }
        data.update(overrides)
        return data

    def test_list_salaries_success(self):
        self.salary()
        response = self.client.get(SALARIES_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_list_salaries_scoped_to_own_branches(self):
        other = self.hire("Boshqa", branch=self.branch2, org=self.org2)
        self.salary(branch=self.branch2, employee=other)
        self.salary()
        response = self.client.get(SALARIES_URL)
        self.assertEqual(response.data["count"], 1)

    def test_list_salaries_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(SALARIES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_salary_success(self):
        response = self.client.post(SALARIES_URL, self.salary_data(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "draft")

    def test_create_salary_ignores_status_input(self):
        response = self.client.post(
            SALARIES_URL, self.salary_data(status="approved"), format="json"
        )
        self.assertEqual(response.data["status"], "draft")

    def test_create_salary_invalid_data(self):
        response = self.client.post(SALARIES_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_salary_negative_amount_invalid_data(self):
        response = self.client.post(
            SALARIES_URL, self.salary_data(amount="-1"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_salary_forbidden_without_permission(self):
        self.client.force_authenticate(self.user_org2)
        response = self.client.post(SALARIES_URL, self.salary_data(), format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_salary_other_branch_employee_invalid_data(self):
        other = self.hire("Boshqa", branch=self.branch2, org=self.org2)
        response = self.client.post(
            SALARIES_URL, self.salary_data(employee=str(other.id)), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_draft_salary_success(self):
        salary = self.salary()
        response = self.client.patch(
            f"{SALARIES_URL}{salary.id}/", {"amount": "3000000.00"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_approved_salary_invalid_data(self):
        salary = self.salary()
        approve_salary(salary)
        response = self.client.patch(
            f"{SALARIES_URL}{salary.id}/", {"amount": "1.00"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_draft_salary_success(self):
        salary = self.salary()
        response = self.client.delete(f"{SALARIES_URL}{salary.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_approved_salary_invalid_data(self):
        salary = self.salary()
        approve_salary(salary)
        response = self.client.delete(f"{SALARIES_URL}{salary.id}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_salaries_by_status_success(self):
        self.salary()
        approved = self.salary(for_month=2)
        approve_salary(approved)
        response = self.client.get(f"{SALARIES_URL}?status=approved")
        self.assertEqual(response.data["count"], 1)


class CalculatingSalaryStatusTestCase(SalaryBaseTestCase):
    def test_approve_salary_success(self):
        salary = self.salary()
        response = self.client.post(f"{SALARIES_URL}{salary.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "approved")

    def test_approve_approved_salary_invalid_data(self):
        salary = self.salary()
        approve_salary(salary)
        response = self.client.post(f"{SALARIES_URL}{salary.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_second_salary_same_month_invalid_data(self):
        approve_salary(self.salary())
        second = self.salary()
        response = self.client.post(f"{SALARIES_URL}{second.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_salary_other_month_success(self):
        approve_salary(self.salary())
        february = self.salary(for_month=2)
        response = self.client.post(f"{SALARIES_URL}{february.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_approve_salary_unauthenticated(self):
        salary = self.salary()
        self.client.force_authenticate(user=None)
        response = self.client.post(f"{SALARIES_URL}{salary.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_salary_not_found(self):
        response = self.client.post(
            f"{SALARIES_URL}00000000-0000-0000-0000-000000000000/approve/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_approved_salary_success(self):
        salary = self.salary()
        approve_salary(salary)
        response = self.client.post(f"{SALARIES_URL}{salary.id}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "cancelled")

    def test_cancel_cancelled_salary_invalid_data(self):
        salary = self.salary()
        cancel_salary(salary)
        response = self.client.post(f"{SALARIES_URL}{salary.id}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_service_success(self):
        result = approve_salary(self.salary())
        self.assertEqual(result.status, CalculatingSalary.Status.APPROVED)

    def test_approve_cancelled_service_raises(self):
        salary = self.salary()
        cancel_salary(salary)
        with self.assertRaises(ValidationError):
            approve_salary(salary)


class CalculateSalaryTestCase(SalaryBaseTestCase):
    def prepare(self, plan_fact=None):
        """Tasdiqlangan tabel va xodim soatlari (standart: 16 soat reja, 12 fakt)."""
        timesheet = self.approved_timesheet()
        self.add_hours(timesheet, self.employee, plan_fact or {10: (8, 8), 11: (8, 4)})
        return timesheet

    def test_calculate_salary_success(self):
        self.prepare()
        response = self.calculate()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["salaries"]), 1)
        salary = CalculatingSalary.objects.get(employee=self.employee)
        # 5 000 000 × 12/16 = 3 750 000
        self.assertEqual(salary.amount, Decimal("3750000.00"))
        self.assertEqual(salary.currency, self.uzs)
        self.assertEqual(salary.currency_amount, Decimal("3750000.00"))
        self.assertEqual(salary.status, CalculatingSalary.Status.DRAFT)

    def test_calculate_salary_caps_hours_at_plan(self):
        self.prepare({10: (8, 12)})
        self.calculate()
        salary = CalculatingSalary.objects.get(employee=self.employee)
        self.assertEqual(salary.amount, Decimal("5000000.00"))

    def test_calculate_salary_adds_accrual_and_subtracts_retention(self):
        self.prepare()
        bonus = self.accrual(
            name="Mukofot",
            type=AccrualRetention.Type.FIX_SUMMA,
            currency=self.usd,
            value=100,
            is_retention=False,
        )
        fine = self.accrual(
            name="Jarima",
            type=AccrualRetention.Type.PERCENT,
            currency=self.uzs,
            value=10,
            is_retention=True,
        )
        self.add_document(bonus)
        self.add_document(fine)
        self.calculate()
        salary = CalculatingSalary.objects.get(employee=self.employee)
        # 3 750 000 + 100 × 12 500 − 10% × 3 750 000 = 4 625 000
        self.assertEqual(salary.amount, Decimal("4625000.00"))

    def test_calculate_salary_ignores_draft_documents(self):
        self.prepare()
        bonus = self.accrual(
            name="Mukofot",
            type=AccrualRetention.Type.FIX_SUMMA,
            currency=self.uzs,
            value=1000000,
        )
        document = self.add_document(bonus)
        document.status = AccrualRetentionDocument.Status.DRAFT
        document.save()
        self.calculate()
        salary = CalculatingSalary.objects.get(employee=self.employee)
        self.assertEqual(salary.amount, Decimal("3750000.00"))

    def test_calculate_salary_never_negative(self):
        self.prepare()
        fine = self.accrual(
            name="Katta jarima",
            type=AccrualRetention.Type.FIX_SUMMA,
            currency=self.uzs,
            value=99000000,
            is_retention=True,
        )
        self.add_document(fine)
        self.calculate()
        salary = CalculatingSalary.objects.get(employee=self.employee)
        self.assertEqual(salary.amount, Decimal("0.00"))

    def test_calculate_salary_missing_rate_invalid_data(self):
        self.prepare()
        CurrencyLedger.objects.all().delete()
        bonus = self.accrual(
            name="Mukofot",
            type=AccrualRetention.Type.FIX_SUMMA,
            currency=self.usd,
            value=100,
        )
        self.add_document(bonus)
        response = self.calculate()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(CalculatingSalary.objects.count(), 0)

    def test_calculate_salary_requires_approved_timesheet_invalid_data(self):
        EmployeeTimesheet.objects.create(branch=self.branch1, for_month=1)
        response = self.calculate()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_calculate_salary_without_uzs_invalid_data(self):
        self.prepare()
        self.uzs.is_active = False
        self.uzs.save()
        response = self.calculate()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_calculate_salary_skips_non_fixed_salary_type(self):
        self.prepare()
        percent_employee = self.hire(
            "Foizli",
            salary_type=RecruitmentDismissal.SalaryType.SALES_PERCENT,
            fix_summa=None,
            fix_percent=10,
        )
        self.add_hours(self.approved_timesheet(), percent_employee, {10: (8, 8)})
        response = self.calculate()
        skipped = {item["employee"]: item for item in response.data["skipped"]}
        self.assertIn(percent_employee.pk, skipped)
        self.assertFalse(
            CalculatingSalary.objects.filter(employee=percent_employee).exists()
        )

    def test_calculate_salary_skips_employee_without_timesheet_hours(self):
        self.prepare()
        no_hours = self.hire("Soatsiz")
        response = self.calculate()
        skipped_ids = [item["employee"] for item in response.data["skipped"]]
        self.assertIn(no_hours.pk, skipped_ids)

    def test_calculate_salary_skips_dismissed_employee(self):
        self.prepare()
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.DISMISSAL,
            branch=self.branch1,
            employee=self.employee,
            position=self.position,
            card_number="8600123456789012",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 5),
            dismissal_reason="O'z xohishi bilan",
        )
        response = self.calculate()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["salaries"], [])

    def test_calculate_salary_again_updates_draft_not_duplicates(self):
        self.prepare()
        self.calculate()
        self.calculate()
        self.assertEqual(CalculatingSalary.objects.count(), 1)

    def test_calculate_salary_skips_employee_with_approved_salary(self):
        self.prepare()
        self.calculate()
        approve_salary(CalculatingSalary.objects.get(employee=self.employee))
        response = self.calculate()
        self.assertEqual(response.data["salaries"], [])
        self.assertEqual(len(response.data["skipped"]), 1)

    def test_calculate_salary_only_own_branch_employees(self):
        self.prepare()
        other = self.hire("Boshqa", branch=self.branch2, org=self.org2)
        self.add_hours(
            self.approved_timesheet(branch=self.branch2), other, {10: (8, 8)}
        )
        self.calculate()
        self.assertFalse(CalculatingSalary.objects.filter(employee=other).exists())

    def test_calculate_salary_service_returns_salaries_and_skipped(self):
        self.prepare()
        salaries, skipped = calculate_salaries(self.branch1, 1, 2026)
        self.assertEqual(len(salaries), 1)
        self.assertEqual(skipped, [])

    def test_calculate_salary_invalid_data(self):
        response = self.client.post(f"{SALARIES_URL}calculate/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_calculate_salary_invalid_month_invalid_data(self):
        response = self.calculate(for_month=13)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_calculate_salary_inaccessible_branch_invalid_data(self):
        response = self.calculate(branch=str(self.branch2.id))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_calculate_salary_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.calculate()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_calculate_salary_forbidden_without_permission(self):
        self.client.force_authenticate(self.user_org2)
        response = self.calculate()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
