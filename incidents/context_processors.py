from .models import Incident


def role_flags(request):
    user = request.user

    # default counts
    admin_assigned = 0
    support_assigned = 0
    user_incidents = 0

    if user.is_authenticated:
        admin_assigned = Incident.objects.filter(assigned_to=user).count()
        support_assigned = Incident.objects.filter(
            assigned_to=user,
            is_visible_to_support=True
        ).count()
        user_incidents = Incident.objects.filter(
            created_by=user,
            is_visible_to_user=True
        ).count()

    return {
        "is_admin": user.is_authenticated and user.is_superuser,
        "is_support": user.is_authenticated and user.groups.filter(name="Support").exists(),
        "admin_assigned_count": admin_assigned,
        "support_assigned_count": support_assigned,
        "user_incident_count": user_incidents,
    }
