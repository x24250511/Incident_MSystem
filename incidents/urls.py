# incidents/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("user/", views.user_dashboard, name="user_dashboard"),
    path("support/", views.support_dashboard, name="support_dashboard"),
    path("admin-view/", views.admin_dashboard, name="admin_dashboard"),

    path("create/", views.create_incident, name="create_incident"),
    path("<int:pk>/", views.incident_detail, name="incident_detail"),
]
