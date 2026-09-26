import datetime

from django.contrib.auth.models import Permission
from rest_framework import status
from rest_framework.exceptions import ValidationError

from apps.finance.models import AccrualRetention, AccrualRetentionDocument, Currency
from apps.finance.services.accrual_document import (
    approve_document,
    cancel_document,
)
from apps.hr.models import Employee, RecruitmentDismissal
from apps.hr.tests.test_hr_api import HRBaseAPITestCase

DOCUMENTS_URL = "/api/v1/finance/accrual-retention-documents/"
DATE = "2026-01-15T10:00:00+05:00"


class AccrualDocumentBaseTestCase(HRBaseAPITestCase):
    def setUp(self):
        super().setUp()
        perms = Permission.objects.filter(
            content_type__app_label="finance",
            codename__in=[
                f"{action}_accrualretentiondocument"
                for action in ("view", "add", "change", "delete")
            ],
        )
        self.role_org1.permissions.add(*perms)
        self.currency = Currency.objects.create(name="So'm", short_name="UZS")
        self.bonus = AccrualRetention.objects.create(
            name="Mukofot",
            type=AccrualRetention.Type.FIX_SUMMA,
            currency=self.currency,
            value=100000,
            is_retention=False,
        )
        self.fine = AccrualRetention.objects.create(
            name="Jarima",
            type=AccrualRetention.Type.FIX_SUMMA,
            currency=self.currency,
            value=50000,
            is_retention=True,
        )
        self.employee = self.hire("Xodim 1")
        self.client.force_authenticate(self.user_org1)

    def hire(self, full_name, branch=None, org=None):
        """Ishlab turgan (ishga olingan) xodim yaratadi."""
        branch = branch or self.branch1
        employee = Employee.objects.create(
            organization=org or self.org1, branch=branch, full_name=full_name
        )
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.RECRUITMENT,
            branch=branch,
            employee=employee,
            position=self.position,
            card_number="8600123456789012",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 1),
        )
        return employee

    def document_data(self, **overrides):
        """Standart to'g'ri hujjat ma'lumotlari."""
        data = {
            "branch": str(self.branch1.id),
            "employee": str(self.employee.id),
            "accrual_retention": str(self.bonus.id),
            "date": DATE,
        }
        data.update(overrides)
        return data

    def create_document(self, **overrides):
        """Qoralama hujjatni to'g'ridan-to'g'ri bazada yaratadi."""
        values = {
            "branch": self.branch1,
            "employee": self.employee,
            "accrual_retention": self.bonus,
            "date": datetime.datetime(
                2026, 1, 15, 10, tzinfo=datetime.timezone(datetime.timedelta(hours=5))
            ),
        }
        values.update(overrides)
        return AccrualRetentionDocument.objects.create(**values)


class AccrualRetentionDocumentAPITestCase(AccrualDocumentBaseTestCase):
    def test_list_documents_success(self):
        self.create_document()
        response = self.client.get(DOCUMENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_list_documents_scoped_to_own_branches(self):
        other = self.hire("Boshqa", branch=self.branch2, org=self.org2)
        self.create_document(branch=self.branch2, employee=other)
        self.create_document()
        response = self.client.get(DOCUMENTS_URL)
        self.assertEqual(response.data["count"], 1)

    def test_list_documents_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(DOCUMENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_document_success(self):
        response = self.client.post(DOCUMENTS_URL, self.document_data(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "draft")

    def test_create_document_ignores_status_input(self):
        response = self.client.post(
            DOCUMENTS_URL, self.document_data(status="approved"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "draft")

    def test_create_document_same_day_twice_success(self):
        self.client.post(DOCUMENTS_URL, self.document_data(), format="json")
        response = self.client.post(DOCUMENTS_URL, self.document_data(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_document_future_date_success(self):
        response = self.client.post(
            DOCUMENTS_URL,
            self.document_data(date="2030-01-15T10:00:00+05:00"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_document_invalid_data(self):
        response = self.client.post(DOCUMENTS_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_document_forbidden_without_permission(self):
        self.client.force_authenticate(self.user_org2)
        response = self.client.post(DOCUMENTS_URL, self.document_data(), format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_document_other_branch_employee_invalid_data(self):
        other = self.hire("Boshqa", branch=self.branch2, org=self.org2)
        response = self.client.post(
            DOCUMENTS_URL, self.document_data(employee=str(other.id)), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_document_inaccessible_branch_invalid_data(self):
        other = self.hire("Boshqa", branch=self.branch2, org=self.org2)
        response = self.client.post(
            DOCUMENTS_URL,
            self.document_data(branch=str(self.branch2.id), employee=str(other.id)),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_document_dismissed_employee_invalid_data(self):
        RecruitmentDismissal.objects.create(
            type=RecruitmentDismissal.Type.DISMISSAL,
            branch=self.branch1,
            employee=self.employee,
            position=self.position,
            card_number="8600123456789012",
            salary_type=RecruitmentDismissal.SalaryType.FIXED_AMOUNT,
            fix_summa=5000000,
            rec_dism_date=datetime.date(2026, 1, 10),
            dismissal_reason="O'z xohishi bilan",
        )
        response = self.client.post(DOCUMENTS_URL, self.document_data(), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_document_not_hired_employee_invalid_data(self):
        not_hired = Employee.objects.create(
            organization=self.org1, branch=self.branch1, full_name="Olinmagan"
        )
        response = self.client.post(
            DOCUMENTS_URL,
            self.document_data(employee=str(not_hired.id)),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_document_inactive_accrual_invalid_data(self):
        self.bonus.is_active = False
        self.bonus.save()
        response = self.client.post(DOCUMENTS_URL, self.document_data(), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_draft_document_success(self):
        document = self.create_document()
        response = self.client.patch(
            f"{DOCUMENTS_URL}{document.id}/",
            {"accrual_retention": str(self.fine.id)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        document.refresh_from_db()
        self.assertEqual(document.accrual_retention, self.fine)

    def test_update_approved_document_invalid_data(self):
        document = self.create_document()
        approve_document(document)
        response = self.client.patch(
            f"{DOCUMENTS_URL}{document.id}/",
            {"accrual_retention": str(self.fine.id)},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_draft_document_success(self):
        document = self.create_document()
        response = self.client.delete(f"{DOCUMENTS_URL}{document.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_approved_document_invalid_data(self):
        document = self.create_document()
        approve_document(document)
        response = self.client.delete(f"{DOCUMENTS_URL}{document.id}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_documents_by_is_retention_success(self):
        self.create_document(accrual_retention=self.bonus)
        self.create_document(accrual_retention=self.fine)
        response = self.client.get(f"{DOCUMENTS_URL}?is_retention=true")
        self.assertEqual(response.data["count"], 1)
        response = self.client.get(f"{DOCUMENTS_URL}?is_retention=false")
        self.assertEqual(response.data["count"], 1)

    def test_filter_documents_by_status_success(self):
        self.create_document()
        approved = self.create_document()
        approve_document(approved)
        response = self.client.get(f"{DOCUMENTS_URL}?status=approved")
        self.assertEqual(response.data["count"], 1)

    def test_filter_documents_by_date_range_success(self):
        self.create_document()
        response = self.client.get(
            f"{DOCUMENTS_URL}?date_from=2026-01-15&date_to=2026-01-15"
        )
        self.assertEqual(response.data["count"], 1)
        response = self.client.get(f"{DOCUMENTS_URL}?date_from=2026-02-01")
        self.assertEqual(response.data["count"], 0)

    def test_approve_document_success(self):
        document = self.create_document()
        response = self.client.post(f"{DOCUMENTS_URL}{document.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "approved")

    def test_approve_approved_document_invalid_data(self):
        document = self.create_document()
        approve_document(document)
        response = self.client.post(f"{DOCUMENTS_URL}{document.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_document_unauthenticated(self):
        document = self.create_document()
        self.client.force_authenticate(user=None)
        response = self.client.post(f"{DOCUMENTS_URL}{document.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_document_not_found(self):
        response = self.client.post(
            f"{DOCUMENTS_URL}00000000-0000-0000-0000-000000000000/approve/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_approved_document_success(self):
        document = self.create_document()
        approve_document(document)
        response = self.client.post(f"{DOCUMENTS_URL}{document.id}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "cancelled")

    def test_cancel_cancelled_document_invalid_data(self):
        document = self.create_document()
        cancel_document(document)
        response = self.client.post(f"{DOCUMENTS_URL}{document.id}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AccrualRetentionDocumentBulkCreateTestCase(AccrualDocumentBaseTestCase):
    def bulk_data(self, employees, **overrides):
        """Ommaviy yaratish uchun standart ma'lumotlar."""
        data = {
            "branch": str(self.branch1.id),
            "accrual_retention": str(self.bonus.id),
            "date": DATE,
            "employees": [str(e.id) for e in employees],
        }
        data.update(overrides)
        return data

    def test_bulk_create_documents_success(self):
        second = self.hire("Xodim 2")
        response = self.client.post(
            f"{DOCUMENTS_URL}bulk-create/",
            self.bulk_data([self.employee, second]),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(AccrualRetentionDocument.objects.count(), 2)

    def test_bulk_create_documents_invalid_data(self):
        response = self.client.post(f"{DOCUMENTS_URL}bulk-create/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bulk_create_documents_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            f"{DOCUMENTS_URL}bulk-create/",
            self.bulk_data([self.employee]),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_bulk_create_documents_forbidden_without_permission(self):
        self.client.force_authenticate(self.user_org2)
        response = self.client.post(
            f"{DOCUMENTS_URL}bulk-create/",
            self.bulk_data([self.employee]),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_bulk_create_documents_duplicate_employee_invalid_data(self):
        response = self.client.post(
            f"{DOCUMENTS_URL}bulk-create/",
            self.bulk_data([self.employee, self.employee]),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bulk_create_documents_empty_list_invalid_data(self):
        response = self.client.post(
            f"{DOCUMENTS_URL}bulk-create/", self.bulk_data([]), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_bulk_create_documents_dismissed_employee_saves_nothing(self):
        not_hired = Employee.objects.create(
            organization=self.org1, branch=self.branch1, full_name="Olinmagan"
        )
        response = self.client.post(
            f"{DOCUMENTS_URL}bulk-create/",
            self.bulk_data([self.employee, not_hired]),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(AccrualRetentionDocument.objects.count(), 0)


class AccrualDocumentServiceTestCase(AccrualDocumentBaseTestCase):
    def test_approve_draft_document_success(self):
        result = approve_document(self.create_document())
        self.assertEqual(result.status, AccrualRetentionDocument.Status.APPROVED)

    def test_approve_cancelled_document_raises(self):
        document = self.create_document()
        cancel_document(document)
        with self.assertRaises(ValidationError):
            approve_document(document)

    def test_cancel_draft_document_success(self):
        result = cancel_document(self.create_document())
        self.assertEqual(result.status, AccrualRetentionDocument.Status.CANCELLED)


class AccrualRetentionIsRetentionAPITestCase(AccrualDocumentBaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.force_authenticate(self.admin)

    def test_create_accrual_retention_with_is_retention_success(self):
        response = self.client.post(
            "/api/v1/finance/accrual-retentions/",
            {
                "name": "Kechikish jarimasi",
                "type": "fix_summa",
                "currency": str(self.currency.id),
                "value": "20000.00",
                "is_retention": True,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["is_retention"])

    def test_filter_accrual_retentions_by_is_retention_success(self):
        response = self.client.get(
            "/api/v1/finance/accrual-retentions/?is_retention=true"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
