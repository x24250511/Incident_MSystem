# incidents/models.py
from django.conf import settings
from django.db import models


class Incident(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("IN_PROGRESS", "In progress"),
        ("RESOLVED", "Resolved"),
    ]

    SEVERITY_CHOICES = [
        ("CRITICAL", "Critical"),
        ("HIGH", "High"),
        ("MEDIUM", "Medium"),
        ("LOW", "Low"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    severity = models.CharField(
        max_length=10,
        choices=SEVERITY_CHOICES,
        default="LOW",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="OPEN",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="incidents_created",
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incidents_assigned",
    )

    is_visible_to_user = models.BooleanField(default=True)
    is_visible_to_support = models.BooleanField(default=True)

    attachment = models.FileField(
        upload_to="attachments/",
        blank=True,
        null=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"


class IncidentComment(models.Model):
    incident = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Comment by {self.author} on {self.incident}"
