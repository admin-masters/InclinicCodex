from datetime import timedelta
import uuid
from django.db import models
from django.utils import timezone


class Campaign(models.Model):
    campaign_id = models.CharField(max_length=32, unique=True, editable=False)
    name = models.CharField(max_length=255)
    brand_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    banner_top_url = models.URLField(blank=True)
    banner_top_target = models.URLField(blank=True)
    banner_bottom_url = models.URLField(blank=True)
    banner_bottom_target = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.campaign_id:
            self.campaign_id = f"CAMP-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.campaign_id} - {self.name}"


class FieldRepresentative(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="field_reps")
    name = models.CharField(max_length=255)
    email = models.EmailField()
    whatsapp_number = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class CampaignCycle(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="cycles")
    cycle_number = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    title = models.CharField(max_length=255)
    message_template = models.TextField()
    reminder_template = models.TextField()
    pdf_url = models.URLField()
    video_vimeo_url = models.URLField()

    class Meta:
        unique_together = ("campaign", "cycle_number")


class Doctor(models.Model):
    whatsapp_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)


class ShareRecord(models.Model):
    STATUS_SENT = "sent"
    STATUS_READ = "read"
    STATUS_CHOICES = [(STATUS_SENT, "Sent"), (STATUS_READ, "Read")]

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    cycle = models.ForeignKey(CampaignCycle, on_delete=models.CASCADE)
    field_rep = models.ForeignKey(FieldRepresentative, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True, editable=False)
    whatsapp_message = models.TextField()
    is_reminder = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_SENT)
    shared_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = uuid.uuid4().hex
        super().save(*args, **kwargs)

    @property
    def reminder_due(self):
        return self.status == self.STATUS_SENT and timezone.now() >= self.shared_at + timedelta(days=6)

    @property
    def button_state(self):
        if self.status == self.STATUS_READ:
            return "green"
        if self.reminder_due:
            return "purple"
        return "yellow"


class ActivityEvent(models.Model):
    EVENT_CHOICES = [
        ("whatsapp_click", "WhatsApp Link Click"),
        ("landing_visit", "Landing Visit"),
        ("pdf_last_page", "PDF Last Page"),
        ("video_progress", "Video Progress"),
        ("pdf_download", "PDF Download"),
    ]
    share = models.ForeignKey(ShareRecord, on_delete=models.CASCADE, related_name="activities")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=30, choices=EVENT_CHOICES)
    value = models.FloatField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
