# incidents/admin.py
from django.contrib import admin
from .models import Incident, IncidentComment


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "severity",
        "status",
        "created_by",
        "assigned_to",
        "is_visible_to_user",
        "is_visible_to_support",
        "created_at",
    )
    list_filter = ("status", "severity", "is_visible_to_user",
                   "is_visible_to_support")
    search_fields = ("title", "description",
                     "created_by__username", "assigned_to__username")


@admin.register(IncidentComment)
class IncidentCommentAdmin(admin.ModelAdmin):
    list_display = ("id", "incident", "author", "created_at")
    search_fields = ("text", "author__username", "incident__title")
