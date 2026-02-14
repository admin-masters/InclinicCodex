import csv
import io
import uuid
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Campaign(TimestampedModel):
    campaign_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    company_name = models.CharField(max_length=255)
    brand_name = models.CharField(max_length=255)
    doctors_expected = models.PositiveIntegerField()
    contact_name = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField()
    desktop_banner = models.URLField(blank=True)
    mobile_banner = models.URLField(blank=True)
    created_by = models.ForeignKey("auth.User", on_delete=models.PROTECT, related_name="campaigns")

    def __str__(self):
        return f"{self.campaign_uuid} - {self.brand_name}"


class SystemType(models.TextChoices):
    RED_FLAG = "red_flag", "Red Flag Alerts System"
    PATIENT = "patient", "Patient Education System"
    INCLINIC = "inclinic", "In-Clinic Education System"


class CampaignSystem(TimestampedModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="systems")
    system_type = models.CharField(max_length=20, choices=SystemType.choices)
    is_enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ("campaign", "system_type")


class InClinicConfiguration(TimestampedModel):
    STATUS_DRAFT = "draft"
    STATUS_ACTIVE = "active"
    STATUS_CHOICES = [(STATUS_DRAFT, "Draft"), (STATUS_ACTIVE, "Active")]

    campaign_system = models.OneToOneField(CampaignSystem, on_delete=models.CASCADE, related_name="inclinic_config")
    in_charge_name = models.CharField(max_length=255)
    in_charge_designation = models.CharField(max_length=255)
    items_per_clinic_per_year = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    contract_file = models.FileField(upload_to="contracts/", blank=True)
    brand_logo = models.URLField(blank=True)
    company_logo = models.URLField(blank=True)
    printing_required = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)


class FieldRepresentative(TimestampedModel):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="field_reps")
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    brand_field_rep_id = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = (
            ("campaign", "email"),
            ("campaign", "phone_number"),
            ("campaign", "brand_field_rep_id"),
        )


class FieldRepRecruitmentLink(TimestampedModel):
    campaign = models.OneToOneField(Campaign, on_delete=models.CASCADE, related_name="recruitment_link")
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    @property
    def shareable_path(self):
        return f"/field-rep/recruit/{self.token}/"


class Collateral(TimestampedModel):
    class Purpose(models.TextChoices):
        DOC_LONG = "doctor_long", "Doctor Education Long"
        DOC_SHORT = "doctor_short", "Doctor Education Short"
        PATIENT_LONG = "patient_long", "Patient Education Long"
        PATIENT_SHORT = "patient_short", "Patient Education Short"

    class ItemType(models.TextChoices):
        PDF = "pdf", "PDF"
        VIDEO = "video", "Video"
        BOTH = "both", "PDF + Video"

    campaign_system = models.ForeignKey(CampaignSystem, on_delete=models.CASCADE, related_name="collaterals")
    cycle_label = models.CharField(max_length=50, default="default")
    purpose = models.CharField(max_length=30, choices=Purpose.choices)
    content_title = models.CharField(max_length=255)
    content_id = models.CharField(max_length=100, blank=True)
    item_type = models.CharField(max_length=10, choices=ItemType.choices)
    pdf_file = models.FileField(upload_to="collaterals/pdf/", blank=True, validators=[FileExtensionValidator(["pdf"])])
    vimeo_url = models.URLField(blank=True)
    banner1 = models.URLField(blank=True)
    banner2 = models.URLField(blank=True)
    doctor_attribution = models.CharField(max_length=255)
    content_description = models.TextField(blank=True)
    webinar_link = models.URLField(blank=True)
    webinar_title = models.CharField(max_length=255, blank=True)
    webinar_description = models.TextField(blank=True)
    webinar_date = models.DateField(null=True, blank=True)
    whatsapp_template = models.TextField(help_text="Supports placeholder $collateralLinks")
    sort_order = models.PositiveIntegerField(default=1)

    def clean(self):
        if self.item_type in [self.ItemType.PDF, self.ItemType.BOTH] and not self.pdf_file:
            raise ValidationError("PDF file is required for selected item type.")
        if self.item_type in [self.ItemType.VIDEO, self.ItemType.BOTH]:
            if not self.vimeo_url:
                raise ValidationError("Vimeo URL is required for selected item type.")
            if "vimeo.com" not in self.vimeo_url:
                raise ValidationError("Video source must be Vimeo.")


class CsvImportResult:
    REQUIRED_HEADERS = ["field-rep-name", "email-id", "phone-number", "brand-supplied-field-rep-id"]

    def __init__(self):
        self.created = 0
        self.errors = []


def import_field_reps_from_csv(campaign: Campaign, csv_bytes: bytes) -> CsvImportResult:
    result = CsvImportResult()
    decoded = csv_bytes.decode("utf-8")
    reader = csv.DictReader(io.StringIO(decoded))
    if reader.fieldnames != CsvImportResult.REQUIRED_HEADERS:
        result.errors.append("Invalid CSV headers. Expected exact columns in required order.")
        return result

    for index, row in enumerate(reader, start=2):
        email = (row.get("email-id") or "").strip().lower()
        phone = (row.get("phone-number") or "").strip()
        brand_id = (row.get("brand-supplied-field-rep-id") or "").strip()
        name = (row.get("field-rep-name") or "").strip()
        if not all([email, phone, brand_id, name]):
            result.errors.append(f"Row {index}: missing mandatory fields")
            continue
        if FieldRepresentative.objects.filter((models.Q(email=email) | models.Q(phone_number=phone) | models.Q(brand_field_rep_id=brand_id)), campaign=campaign).exists():
            result.errors.append(f"Row {index}: duplicate rep within campaign")
            continue
        FieldRepresentative.objects.create(
            campaign=campaign,
            full_name=name,
            email=email,
            phone_number=phone,
            brand_field_rep_id=brand_id,
        )
        result.created += 1
    return result
