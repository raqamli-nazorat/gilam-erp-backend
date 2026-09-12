from ..models import Organization


def get_organization_status_counts():
    active_qs = Organization.objects.active()
    return {
        "active": active_qs.filter(is_suspended=False).count(),
        "suspended": active_qs.filter(is_suspended=True).count(),
    }
