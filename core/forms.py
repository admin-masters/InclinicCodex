from django import forms
from .models import Campaign, Collateral, InClinicConfiguration, SystemType


class CampaignCreateForm(forms.ModelForm):
    systems = forms.MultipleChoiceField(
        choices=SystemType.choices,
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )
    field_rep_csv = forms.FileField(required=False, help_text="CSV with headers: field-rep-name,email-id,phone-number,brand-supplied-field-rep-id")

    class Meta:
        model = Campaign
        fields = [
            "company_name",
            "brand_name",
            "doctors_expected",
            "contact_name",
            "contact_phone",
            "contact_email",
            "desktop_banner",
            "mobile_banner",
        ]


class InClinicConfigurationForm(forms.ModelForm):
    class Meta:
        model = InClinicConfiguration
        fields = [
            "in_charge_name",
            "in_charge_designation",
            "items_per_clinic_per_year",
            "start_date",
            "end_date",
            "contract_file",
            "brand_logo",
            "company_logo",
            "printing_required",
            "description",
            "status",
        ]


class CollateralForm(forms.ModelForm):
    class Meta:
        model = Collateral
        fields = [
            "cycle_label",
            "purpose",
            "content_title",
            "content_id",
            "item_type",
            "pdf_file",
            "vimeo_url",
            "banner1",
            "banner2",
            "doctor_attribution",
            "content_description",
            "webinar_link",
            "webinar_title",
            "webinar_description",
            "webinar_date",
            "whatsapp_template",
            "sort_order",
        ]

    def clean_vimeo_url(self):
        value = self.cleaned_data.get("vimeo_url", "")
        if value and "vimeo.com" not in value:
            raise forms.ValidationError("Video source must be Vimeo.")
        return value
