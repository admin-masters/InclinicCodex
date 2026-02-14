from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from core.models import Campaign, CampaignSystem, Collateral, InClinicConfiguration, SystemType, FieldRepresentative


@override_settings(USE_SQLITE="1")
class PublisherFlowTests(TestCase):
    databases = {"default", "reporting"}

    def setUp(self):
        self.publisher_group = Group.objects.create(name="Publisher")
        self.publisher = User.objects.create_user(username="publisher", password="pass123")
        self.publisher.groups.add(self.publisher_group)
        self.non_publisher = User.objects.create_user(username="other", password="pass123")

    def login_publisher(self):
        self.client.login(username="publisher", password="pass123")

    def test_role_restricted_dashboard(self):
        self.client.login(username="other", password="pass123")
        response = self.client.get(reverse("publisher_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_campaign_creation_with_systems_and_csv(self):
        self.login_publisher()
        csv_content = (
            "field-rep-name,email-id,phone-number,brand-supplied-field-rep-id\n"
            "Rep One,rep1@example.com,999001,B001\n"
        ).encode()
        csv_file = SimpleUploadedFile("reps.csv", csv_content, content_type="text/csv")

        response = self.client.post(reverse("campaign_add"), {
            "company_name": "ABC Pharma",
            "brand_name": "CardioMax",
            "doctors_expected": 200,
            "contact_name": "Jane",
            "contact_phone": "9999999999",
            "contact_email": "jane@example.com",
            "desktop_banner": "https://example.com/d.jpg",
            "mobile_banner": "https://example.com/m.jpg",
            "systems": [SystemType.INCLINIC, SystemType.RED_FLAG],
            "field_rep_csv": csv_file,
        })
        self.assertEqual(response.status_code, 302)

        campaign = Campaign.objects.get()
        self.assertIsNotNone(campaign.campaign_uuid)
        self.assertEqual(campaign.systems.count(), 2)
        self.assertTrue(campaign.systems.filter(system_type=SystemType.INCLINIC).exists())
        self.assertEqual(FieldRepresentative.objects.filter(campaign=campaign).count(), 1)
        self.assertIsNotNone(campaign.recruitment_link)

    def test_invalid_csv_headers(self):
        self.login_publisher()
        bad_csv = SimpleUploadedFile("bad.csv", b"x,y,z\n1,2,3\n", content_type="text/csv")
        self.client.post(reverse("campaign_add"), {
            "company_name": "ABC Pharma",
            "brand_name": "CardioMax",
            "doctors_expected": 200,
            "contact_name": "Jane",
            "contact_phone": "9999999999",
            "contact_email": "jane@example.com",
            "systems": [SystemType.INCLINIC],
            "field_rep_csv": bad_csv,
        })
        self.assertEqual(FieldRepresentative.objects.count(), 0)

    def create_inclinic_campaign(self):
        campaign = Campaign.objects.create(
            company_name="ABC Pharma",
            brand_name="CardioMax",
            doctors_expected=50,
            contact_name="Jane",
            contact_phone="999",
            contact_email="jane@example.com",
            created_by=self.publisher,
        )
        CampaignSystem.objects.create(campaign=campaign, system_type=SystemType.INCLINIC)
        return campaign

    def test_inclinic_configuration_manual_activation(self):
        self.login_publisher()
        campaign = self.create_inclinic_campaign()
        response = self.client.post(reverse("inclinic_configure", args=[campaign.campaign_uuid]), {
            "in_charge_name": "Manager",
            "in_charge_designation": "Lead",
            "items_per_clinic_per_year": 12,
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "brand_logo": "https://example.com/brand.png",
            "company_logo": "https://example.com/company.png",
            "printing_required": "on",
            "description": "Description",
            "status": "draft",
        })
        self.assertEqual(response.status_code, 302)
        config = InClinicConfiguration.objects.get()
        self.assertEqual(config.status, "draft")

        response = self.client.post(reverse("inclinic_configure", args=[campaign.campaign_uuid]), {
            "in_charge_name": "Manager",
            "in_charge_designation": "Lead",
            "items_per_clinic_per_year": 12,
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
            "brand_logo": "https://example.com/brand.png",
            "company_logo": "https://example.com/company.png",
            "description": "Description",
            "status": "active",
        })
        config.refresh_from_db()
        self.assertEqual(config.status, "active")

    def test_collateral_create_and_preview_order(self):
        self.login_publisher()
        campaign = self.create_inclinic_campaign()
        system = campaign.systems.get(system_type=SystemType.INCLINIC)
        response = self.client.post(reverse("collateral_add", args=[campaign.campaign_uuid]), {
            "cycle_label": "C1",
            "purpose": "doctor_long",
            "content_title": "Heart Case",
            "content_id": "CID123",
            "item_type": "both",
            "pdf_file": pdf,
            "vimeo_url": "https://vimeo.com/123456",
            "banner1": "https://example.com/top.jpg",
            "banner2": "https://example.com/bottom.jpg",
            "doctor_attribution": "A. Doctor",
            "content_description": "Desc",
            "whatsapp_template": "Hello $collateralLinks",
            "sort_order": 1,
        })
        self.assertEqual(response.status_code, 302)
        collateral = Collateral.objects.get(campaign_system=system)

        preview = self.client.get(reverse("collateral_preview", args=[collateral.id]))
        self.assertContains(preview, "Shared by")
        self.assertContains(preview, "Download PDF")

    def test_vimeo_validation(self):
        self.login_publisher()
        campaign = self.create_inclinic_campaign()
        response = self.client.post(reverse("collateral_add", args=[campaign.campaign_uuid]), {
            "cycle_label": "C1",
            "purpose": "doctor_long",
            "content_title": "Heart Case",
            "item_type": "video",
            "vimeo_url": "https://youtube.com/watch?v=x",
            "doctor_attribution": "A. Doctor",
            "whatsapp_template": "Hello $collateralLinks",
            "sort_order": 1,
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Video source must be Vimeo")

    def test_all_records_on_default_db(self):
        self.login_publisher()
        self.client.post(reverse("campaign_add"), {
            "company_name": "ABC Pharma",
            "brand_name": "CardioMax",
            "doctors_expected": 200,
            "contact_name": "Jane",
            "contact_phone": "9999999999",
            "contact_email": "jane@example.com",
            "systems": [SystemType.INCLINIC],
        })
        self.assertEqual(Campaign.objects.using("default").count(), 1)
        self.assertEqual(Campaign.objects.using("reporting").count(), 0)
