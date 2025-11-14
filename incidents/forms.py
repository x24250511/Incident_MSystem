# incidents/forms.py
from django import forms
from .models import Incident, IncidentComment


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ["title", "description", "severity", "attachment"]


class CommentForm(forms.ModelForm):
    class Meta:
        model = IncidentComment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={"rows": 3}),
        }
