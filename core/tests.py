from datetime import timedelta
from io import StringIO
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from core.db_router import TransactionReportingRouter
from core.models import ActivityEvent, Campaign, CampaignCycle, Doctor, FieldRepresentative, ShareRecord
from reporting.models import ActivityEventReport


@override_settings(USE_TZ=True)
class WorkflowTests(TestCase):
    databases = {"default", "reporting"}

    def setUp(self):
        self.campaign = Campaign.objects.create(
            name="Cardio CME",
            brand_name="BrandX",
            start_date=timezone.now().date() - timedelta(days=30),
            end_date=timezone.now().date() + timedelta(days=30),
        )
        self.cycle = CampaignCycle.objects.create(
            campaign=self.campaign,
            cycle_number=1,
            start_date=timezone.now().date() - timedelta(days=10),
            end_date=timezone.now().date() + timedelta(days=10),
            title="Cycle1",
            message_template="Please review CME",
            reminder_template="Reminder CME",
            pdf_url="https://example.com/doc.pdf",
            video_vimeo_url="https://player.vimeo.com/video/123",
        )
        self.rep = FieldRepresentative.objects.create(
            campaign=self.campaign, name="Rep", email="rep@example.com", whatsapp_number="911111111111"
        )

    def test_campaign_auto_id(self):
        self.assertTrue(self.campaign.campaign_id.startswith("CAMP-"))

    def test_share_and_doctor_validation_flow(self):
        resp = self.client.post(reverse("share_collateral"), {
            "field_rep_id": self.rep.id,
            "cycle_id": self.cycle.id,
            "doctor_whatsapp": "919900000001",
        })
        self.assertEqual(resp.status_code, 200)
        share = ShareRecord.objects.get()

        mismatch = self.client.post(reverse("doctor_verify", args=[share.token]), {"whatsapp_number": "1"})
        self.assertEqual(mismatch.status_code, 400)

        verify = self.client.post(reverse("doctor_verify", args=[share.token]), {"whatsapp_number": "919900000001"})
        self.assertEqual(verify.status_code, 302)

        landing = self.client.get(reverse("doctor_landing", args=[share.token]))
        self.assertEqual(landing.status_code, 200)
        share.refresh_from_db()
        self.assertEqual(share.status, ShareRecord.STATUS_READ)

    def test_button_color_state_logic(self):
        doctor = Doctor.objects.create(whatsapp_number="919900000002")
        share = ShareRecord.objects.create(
            campaign=self.campaign, cycle=self.cycle, field_rep=self.rep, doctor=doctor, whatsapp_message="x"
        )
        self.assertEqual(share.button_state, "yellow")
        share.shared_at = timezone.now() - timedelta(days=7)
        share.save(update_fields=["shared_at"])
        share.refresh_from_db()
        self.assertEqual(share.button_state, "purple")
        share.status = ShareRecord.STATUS_READ
        share.save(update_fields=["status"])
        self.assertEqual(share.button_state, "green")

    def test_activity_tracking_event_endpoint(self):
        doctor = Doctor.objects.create(whatsapp_number="919900000003")
        share = ShareRecord.objects.create(
            campaign=self.campaign, cycle=self.cycle, field_rep=self.rep, doctor=doctor, whatsapp_message="x"
        )
        response = self.client.post(reverse("track_activity", args=[share.id, "video_progress"]), {"value": 85})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ActivityEvent.objects.count(), 1)

    def test_router_behavior(self):
        router = TransactionReportingRouter()
        self.assertEqual(router.db_for_read(ActivityEvent), "default")
        self.assertEqual(router.db_for_read(ActivityEventReport), "reporting")

    def test_cron_sync_moves_events(self):
        doctor = Doctor.objects.create(whatsapp_number="919900000004")
        share = ShareRecord.objects.create(
            campaign=self.campaign, cycle=self.cycle, field_rep=self.rep, doctor=doctor, whatsapp_message="x"
        )
        ActivityEvent.objects.create(share=share, doctor=doctor, event_type="pdf_download")

        out = StringIO()
        call_command("sync_reporting", stdout=out)
        self.assertIn("Moved 1 events", out.getvalue())
        self.assertEqual(ActivityEvent.objects.using("default").count(), 0)
        self.assertEqual(ActivityEventReport.objects.using("reporting").count(), 1)
