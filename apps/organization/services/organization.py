from ..models import Organization


def get_organization_status_counts():
    return {
        "active": Organization.objects.active().count(),
        "inactive": Organization.objects.inactive().count(),
    }
