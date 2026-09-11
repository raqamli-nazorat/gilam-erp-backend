from ..models import Branch


def get_branch_status_counts():
    """Faol va yopilgan filiallar sonini qaytaradi."""
    return {
        "active": Branch.objects.active().count(),
        "inactive": Branch.objects.inactive().count(),
    }
