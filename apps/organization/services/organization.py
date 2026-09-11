from ..models import Organization


def get_organization_status_counts():
    """Faol va to'xtatilgan tashkilotlar sonini qaytaradi."""
    return {
        "active": Organization.objects.active().count(),
        "inactive": Organization.objects.inactive().count(),
    }
