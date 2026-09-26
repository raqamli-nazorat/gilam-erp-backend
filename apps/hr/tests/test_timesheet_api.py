import datetime

from django.contrib.auth.models import Permission
from rest_framework import status
from rest_framework.exceptions import ValidationError

from apps.hr.models import Employee, EmployeeTimesheet, EmployeeTimesheetItem
from apps.hr.services.timesheet import approve_timesheet, cancel_timesheet

from .test_hr_api import HRBaseAPITestCase

TIMESHEETS_URL = "/api/v1/hr/timesheets/"
ITEMS_URL = "/api/v1/hr/timesheet-items/"
JAN_10 = datetime.datetime(
    2026, 1, 10, tzinfo=datetime.timezone(datetime.timedelta(hours=5))
)


class TimesheetBaseTestCase(HRBaseAPITestCase):
    def setUp(self):
        super().setUp()
        perms = Permission.objects.filter(
            content_type__app_label="hr",
            codename__in=[
                f"{action}_{model}"
                for action in ("view", "add", "change", "delete")
                for model in ("employeetimesheet", "employeetimesheetitem")
            ],
        )
        self.role_org1.permissions.add(*perms)
        self.employee = Employee.objects.create(
            organization=self.org1, branch=self.branch1, full_name="Xodim 1"
        )
        self.timesheet = EmployeeTimesheet.objects.create(
            branch=self.branch1, for_month=EmployeeTimesheet.Month.JANUARY
        )
        self.client.force_authenticate(self.user_org1)

    def item_data(self, **overrides):
        """Standart to'g'ri qator ma'lumotlari."""
        data = {
            "employee_timesheet": str(self.timesheet.id),
            "employee": str(self.employee.id),
            "date": "2026-01-10T00:00:00+05:00",
            "work_hour_in_plan": "8.00",
            "input_date": "2026-01-10T09:00:00+05:00",
            "output_lunch_date": "2026-01-10T13:00:00+05:00",
            "input_lunch_date": "2026-01-10T14:00:00+05:00",
            "output_date": "2026-01-10T18:00:00+05:00",
        }
        data.update(overrides)
        return data


class EmployeeTimesheetAPITestCase(TimesheetBaseTestCase):
    def test_list_timesheets_success(self):
        response = self.client.get(TIMESHEETS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["items_count"], 0)

    def test_list_timesheets_scoped_to_own_branches(self):
        EmployeeTimesheet.objects.create(branch=self.branch2, for_month=2)
        response = self.client.get(TIMESHEETS_URL)
        self.assertEqual(response.data["count"], 1)

    def test_list_timesheets_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(TIMESHEETS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_timesheet_success(self):
        response = self.client.post(
            TIMESHEETS_URL,
            {"branch": str(self.branch1.id), "for_month": 2},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "draft")

    def test_create_timesheet_invalid_data(self):
        response = self.client.post(TIMESHEETS_URL, {"for_month": 13}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_timesheet_ignores_status_input(self):
        response = self.client.post(
            TIMESHEETS_URL,
            {"branch": str(self.branch1.id), "for_month": 3, "status": "approved"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "draft")

    def test_create_timesheet_forbidden_without_permission(self):
        self.client.force_authenticate(self.user_org2)
        response = self.client.post(
            TIMESHEETS_URL,
            {"branch": str(self.branch2.id), "for_month": 2},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_approve_timesheet_success(self):
        response = self.client.post(f"{TIMESHEETS_URL}{self.timesheet.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.timesheet.refresh_from_db()
        self.assertEqual(self.timesheet.status, EmployeeTimesheet.Status.APPROVED)

    def test_approve_approved_timesheet_invalid_data(self):
        approve_timesheet(self.timesheet)
        response = self.client.post(f"{TIMESHEETS_URL}{self.timesheet.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_approve_timesheet_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(f"{TIMESHEETS_URL}{self.timesheet.id}/approve/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_approve_timesheet_not_found(self):
        response = self.client.post(
            f"{TIMESHEETS_URL}00000000-0000-0000-0000-000000000000/approve/"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cancel_approved_timesheet_success(self):
        approve_timesheet(self.timesheet)
        response = self.client.post(f"{TIMESHEETS_URL}{self.timesheet.id}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.timesheet.refresh_from_db()
        self.assertEqual(self.timesheet.status, EmployeeTimesheet.Status.CANCELLED)

    def test_cancel_cancelled_timesheet_invalid_data(self):
        cancel_timesheet(self.timesheet)
        response = self.client.post(f"{TIMESHEETS_URL}{self.timesheet.id}/cancel/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_approved_timesheet_invalid_data(self):
        approve_timesheet(self.timesheet)
        response = self.client.patch(
            f"{TIMESHEETS_URL}{self.timesheet.id}/", {"for_month": 5}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_draft_timesheet_success(self):
        response = self.client.delete(f"{TIMESHEETS_URL}{self.timesheet.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_approved_timesheet_invalid_data(self):
        approve_timesheet(self.timesheet)
        response = self.client.delete(f"{TIMESHEETS_URL}{self.timesheet.id}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_filter_timesheets_by_status_success(self):
        EmployeeTimesheet.objects.create(
            branch=self.branch1, for_month=2, status=EmployeeTimesheet.Status.APPROVED
        )
        response = self.client.get(f"{TIMESHEETS_URL}?status=approved")
        self.assertEqual(response.data["count"], 1)


class TimesheetServiceTestCase(TimesheetBaseTestCase):
    def test_approve_draft_timesheet_success(self):
        result = approve_timesheet(self.timesheet)
        self.assertEqual(result.status, EmployeeTimesheet.Status.APPROVED)

    def test_approve_cancelled_timesheet_raises(self):
        cancel_timesheet(self.timesheet)
        with self.assertRaises(ValidationError):
            approve_timesheet(self.timesheet)

    def test_cancel_draft_timesheet_success(self):
        result = cancel_timesheet(self.timesheet)
        self.assertEqual(result.status, EmployeeTimesheet.Status.CANCELLED)


class EmployeeTimesheetItemAPITestCase(TimesheetBaseTestCase):
    def test_create_item_success(self):
        response = self.client.post(ITEMS_URL, self.item_data(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_item_calculates_fact_hours_success(self):
        response = self.client.post(ITEMS_URL, self.item_data(), format="json")
        item = EmployeeTimesheetItem.objects.get(pk=response.data["id"])
        # 9 soat − 1 soat tushlik = 8 soat
        self.assertEqual(str(item.work_hour_in_fact), "8.00")

    def test_create_item_keeps_manual_fact_hours_success(self):
        response = self.client.post(
            ITEMS_URL, self.item_data(work_hour_in_fact="7.50"), format="json"
        )
        item = EmployeeTimesheetItem.objects.get(pk=response.data["id"])
        self.assertEqual(str(item.work_hour_in_fact), "7.50")

    def test_create_item_invalid_data(self):
        response = self.client.post(ITEMS_URL, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_item_unauthenticated(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(ITEMS_URL, self.item_data(), format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_item_wrong_month_invalid_data(self):
        response = self.client.post(
            ITEMS_URL,
            self.item_data(date="2026-02-10T00:00:00+05:00"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_item_other_branch_employee_invalid_data(self):
        other = Employee.objects.create(
            organization=self.org2, branch=self.branch2, full_name="Boshqa"
        )
        response = self.client.post(
            ITEMS_URL, self.item_data(employee=str(other.id)), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_item_duplicate_day_invalid_data(self):
        self.client.post(ITEMS_URL, self.item_data(), format="json")
        response = self.client.post(ITEMS_URL, self.item_data(), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_item_lunch_order_invalid_data(self):
        response = self.client.post(
            ITEMS_URL,
            self.item_data(input_lunch_date="2026-01-10T12:00:00+05:00"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_item_only_one_lunch_time_invalid_data(self):
        response = self.client.post(
            ITEMS_URL, self.item_data(input_lunch_date=None), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_item_in_approved_timesheet_invalid_data(self):
        approve_timesheet(self.timesheet)
        response = self.client.post(ITEMS_URL, self.item_data(), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_item_in_approved_timesheet_invalid_data(self):
        item = self.create_item()
        approve_timesheet(self.timesheet)
        response = self.client.patch(
            f"{ITEMS_URL}{item.id}/", {"work_hour_in_plan": "6.00"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_item_success(self):
        item = self.create_item()
        response = self.client.delete(f"{ITEMS_URL}{item.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_item_in_approved_timesheet_invalid_data(self):
        item = self.create_item()
        approve_timesheet(self.timesheet)
        response = self.client.delete(f"{ITEMS_URL}{item.id}/")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_items_scoped_to_own_branches(self):
        self.create_item()
        other_employee = Employee.objects.create(
            organization=self.org2, branch=self.branch2, full_name="Boshqa"
        )
        other_timesheet = EmployeeTimesheet.objects.create(
            branch=self.branch2, for_month=1
        )
        EmployeeTimesheetItem.objects.create(
            employee_timesheet=other_timesheet,
            employee=other_employee,
            date=JAN_10,
        )
        response = self.client.get(ITEMS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def create_item(self):
        """Tabelga bitta qator qo'shadi."""
        return EmployeeTimesheetItem.objects.create(
            employee_timesheet=self.timesheet,
            employee=self.employee,
            date=JAN_10,
        )
