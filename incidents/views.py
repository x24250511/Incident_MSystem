# incidents/views.py
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from .forms import IncidentForm, CommentForm
from .models import Incident


def is_support_user(user) -> bool:
    return user.is_authenticated and user.groups.filter(name="Support").exists()


def is_admin_user(user) -> bool:
    return user.is_authenticated and user.is_superuser


def is_support_or_admin(user) -> bool:
    return is_support_user(user) or is_admin_user(user)


@login_required
def login_redirect(request):  # Redirect based on role
    user = request.user
    if user.is_superuser:
        return redirect("admin_dashboard")
    if is_support_user(user):
        return redirect("support_dashboard")
    return redirect("user_dashboard")


@login_required
def logout_view(request):   # Logout and redirect to login
    logout(request)
    return redirect("login")


@login_required
def user_dashboard(request):     # User-facing portal: report incident + list own incidents
    incidents = Incident.objects.filter(    # Only incidents created by this user and visible
        created_by=request.user,
        is_visible_to_user=True,
    ).order_by("-created_at")   # Most recent first

    return render(
        request,
        "incidents/user_dashboard.html",
        {"incidents": incidents},
    )


@login_required
@user_passes_test(is_support_or_admin)
def support_dashboard(request):
    # Only incidents assigned to the logged-in support user
    incidents = Incident.objects.filter(    # Only assigned and visible to support
        assigned_to=request.user,
        is_visible_to_support=True,
    ).order_by("-created_at")

    # Simple metrics for this support user
    total_incidents = incidents.count()   # Total assigned incidents
    critical_count = incidents.filter(severity="CRITICAL").count()   # Critical severity incidents
    open_count = incidents.filter(status="OPEN").count()   # Open status incidents
    resolved_count = incidents.filter(status="RESOLVED").count()   # Resolved status incidents

    # Handle close from support dashboard
    if request.method == "POST":
        incident_id = request.POST.get("incident_id")  # ID of incident to close
        action = request.POST.get("action")

        incident = get_object_or_404(   # Ensure incident belongs to this support user
            Incident, pk=incident_id, assigned_to=request.user)  # Only assigned and visible to support

        if action == "close":  # Close action
            incident.status = "RESOLVED"  # Set status to RESOLVED
            incident.is_visible_to_user = False
            incident.is_visible_to_support = False
            incident.save()
            messages.success(request, "Incident closed.")  # Success message
            return redirect("support_dashboard")

    return render(  # Render support dashboard template
        request,
        "incidents/support_dashboard.html",
        {
            "incidents": incidents,
            "total_incidents": total_incidents,
            "critical_count": critical_count,
            "open_count": open_count,
            "resolved_count": resolved_count,
        },
    )


@login_required
@user_passes_test(is_admin_user)    # Admin view of incidents assigned to self
def admin_my_incidents(request):
    incidents = Incident.objects.filter(
        assigned_to=request.user
    ).order_by("-created_at")

    return render(
        request,
        "incidents/support_dashboard.html",
        {"incidents": incidents},
    )


@login_required
@user_passes_test(is_admin_user)
def admin_dashboard(request):   # Admin overview of all incidents with inline update
    # Handle inline updates
    if request.method == "POST":
        incident_id = request.POST.get("incident_id")
        action = request.POST.get("action")

        incident = get_object_or_404(Incident, pk=incident_id)  # Admin can access all incidents

        # UPDATE (Assign + Status)
        if action == "update":
            assigned_to_id = request.POST.get("assigned_to")
            status = request.POST.get("status")

            #  Assignment LOCK: only assign if NONE
            if incident.assigned_to is None:
                if assigned_to_id:
                    assigned_user = get_object_or_404(User, id=assigned_to_id)
                    incident.assigned_to = assigned_user
            # else → ignore reassignment completely

            # Status can still change
            if status in ["OPEN", "IN_PROGRESS", "RESOLVED"]:
                incident.status = status

            # Special case: resolved hides from user + support
            if incident.status == "RESOLVED":
                incident.is_visible_to_user = False
                incident.is_visible_to_support = False

            incident.save()
            messages.success(request, "Incident updated.")
            return redirect("admin_dashboard")

        # CLOSE incident (force RESOLVED)
        if action == "close":
            incident.status = "RESOLVED"
            incident.is_visible_to_user = False
            incident.is_visible_to_support = False
            incident.save()
            messages.success(request, "Incident closed.")
            return redirect("admin_dashboard")

    # Filters
    status_filter = request.GET.get("status", "")
    severity_filter = request.GET.get("severity", "")

    incidents = Incident.objects.all().order_by("-created_at")

    if status_filter:
        incidents = incidents.filter(status=status_filter)
    if severity_filter:
        incidents = incidents.filter(severity=severity_filter)

    # Stats
    total_incidents = Incident.objects.count()
    critical_count = Incident.objects.filter(severity="CRITICAL").count()
    open_count = Incident.objects.filter(status="OPEN").count()
    resolved_count = Incident.objects.filter(status="RESOLVED").count()

    support_users = User.objects.filter(groups__name="Support")

    return render(
        request,
        "incidents/admin_dashboard.html",
        {
            "incidents": incidents,
            "support_users": support_users,
            "total_incidents": total_incidents,
            "critical_count": critical_count,
            "open_count": open_count,
            "resolved_count": resolved_count,
            "status_filter": status_filter,
            "severity_filter": severity_filter,
        },
    )


@login_required
def create_incident(request):    # Handle incident creation form submission
    if request.method == "POST":
        form = IncidentForm(request.POST, request.FILES)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.created_by = request.user
            incident.status = "OPEN"
            incident.save()
            messages.success(request, "Incident created.")
            if is_admin_user(request.user):
                return redirect("admin_dashboard")
            if is_support_user(request.user):
                return redirect("support_dashboard")
            return redirect("user_dashboard")
    else:
        form = IncidentForm()

    # Fallback simple template (if you hit /incidents/create/ directly)
    return render(
        request,
        "incidents/create_incident.html",
        {"form": form},
    )


@login_required
def incident_detail(request, pk: int):
    incident = get_object_or_404(Incident, pk=pk)

    # visibility rules: admin sees all, support sees assigned, user sees own & visible
    if not is_admin_user(request.user):
        if is_support_user(request.user):
            if incident.assigned_to != request.user or not incident.is_visible_to_support:
                messages.error(
                    request, "You are not allowed to view this incident.")
                return redirect("support_dashboard")
        else:
            if incident.created_by != request.user or not incident.is_visible_to_user:
                messages.error(
                    request, "You are not allowed to view this incident.")
                return redirect("user_dashboard")

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.incident = incident
            comment.author = request.user
            comment.save()
            messages.success(request, "Comment added.")
            return redirect("incident_detail", pk=pk)
    else:
        form = CommentForm()

    return render(
        request,
        "incidents/incident_detail.html",
        {
            "incident": incident,
            "comments": incident.comments.all().order_by("-created_at"),
            "form": form,
        },
    )


@login_required
def close_incident(request, pk: int):
    incident = get_object_or_404(Incident, pk=pk)

    # Only admin or assigned support can close
    if not (
        is_admin_user(request.user)
        or (is_support_user(request.user) and incident.assigned_to == request.user)
    ):
        messages.error(request, "You are not allowed to close this incident.")
        return redirect("user_dashboard")

    if request.method == "POST":
        incident.status = "RESOLVED"
        incident.is_visible_to_user = False
        incident.is_visible_to_support = False
        incident.save()
        messages.success(request, "Incident closed.")

        if is_admin_user(request.user):
            return redirect("admin_dashboard")
        if is_support_user(request.user):
            return redirect("support_dashboard")

    return render(
        request,
        "incidents/close_incident.html",
        {"incident": incident},
    )
