from ..models import Branch


def get_branch_status_counts():
    active_qs = Branch.objects.active()
    return {
        "active": active_qs.filter(is_closed=False).count(),
        "closed": active_qs.filter(is_closed=True).count(),
    }
