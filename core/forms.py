from django import forms
from .models import Campaign, CampaignCycle, FieldRepresentative


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = [
            "name", "brand_name", "description", "start_date", "end_date",
            "banner_top_url", "banner_top_target", "banner_bottom_url", "banner_bottom_target",
        ]


class CampaignCycleForm(forms.ModelForm):
    class Meta:
        model = CampaignCycle
        exclude = ["campaign"]


class FieldRepForm(forms.ModelForm):
    class Meta:
        model = FieldRepresentative
        fields = ["name", "email", "whatsapp_number", "is_active"]
