# incidents/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("user/", views.user_dashboard, name="user_dashboard"),  # User-specific dashboard
    path("support/", views.support_dashboard, name="support_dashboard"),  # Support team dashboard
    path("admin-view/", views.admin_dashboard, name="admin_dashboard"),
    path("admin-my-incidents/", views.admin_my_incidents, name="admin_my_incidents"),

    path("create/", views.create_incident, name="create_incident"),
    path("<int:pk>/", views.incident_detail, name="incident_detail"),
]
