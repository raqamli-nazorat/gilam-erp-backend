from ..models import Branch


def get_branch_status_counts():
    return {
        "active": Branch.objects.active().count(),
        "inactive": Branch.objects.inactive().count(),
    }
