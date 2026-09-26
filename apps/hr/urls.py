from rest_framework.routers import DefaultRouter

from .views import (
    CalculatingSalaryViewSet,
    EmployeeLedgerViewSet,
    EmployeeTimesheetItemViewSet,
    EmployeeTimesheetViewSet,
    EmployeeViewSet,
    PositionViewSet,
    RecruitmentDismissalViewSet,
    WorkScheduleItemViewSet,
    WorkScheduleViewSet,
)

router = DefaultRouter()
router.register("positions", PositionViewSet, basename="position")
router.register("employees", EmployeeViewSet, basename="employee")
router.register("work-schedules", WorkScheduleViewSet, basename="work-schedule")
router.register(
    "work-schedule-items", WorkScheduleItemViewSet, basename="work-schedule-item"
)
router.register(
    "recruitment-dismissals",
    RecruitmentDismissalViewSet,
    basename="recruitment-dismissal",
)
router.register("employee-ledgers", EmployeeLedgerViewSet, basename="employee-ledger")
router.register(
    "calculating-salaries", CalculatingSalaryViewSet, basename="calculating-salary"
)
router.register("timesheets", EmployeeTimesheetViewSet, basename="timesheet")
router.register(
    "timesheet-items", EmployeeTimesheetItemViewSet, basename="timesheet-item"
)

urlpatterns = router.urls
