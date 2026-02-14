from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('campaign_uuid', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('company_name', models.CharField(max_length=255)),
                ('brand_name', models.CharField(max_length=255)),
                ('doctors_expected', models.PositiveIntegerField()),
                ('contact_name', models.CharField(max_length=255)),
                ('contact_phone', models.CharField(max_length=20)),
                ('contact_email', models.EmailField(max_length=254)),
                ('desktop_banner', models.URLField(blank=True)),
                ('mobile_banner', models.URLField(blank=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='campaigns', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CampaignSystem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('system_type', models.CharField(choices=[('red_flag', 'Red Flag Alerts System'), ('patient', 'Patient Education System'), ('inclinic', 'In-Clinic Education System')], max_length=20)),
                ('is_enabled', models.BooleanField(default=True)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='systems', to='core.campaign')),
            ],
            options={'unique_together': {('campaign', 'system_type')}},
        ),
        migrations.CreateModel(
            name='FieldRepRecruitmentLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('campaign', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='recruitment_link', to='core.campaign')),
            ],
        ),
        migrations.CreateModel(
            name='FieldRepresentative',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('full_name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=20)),
                ('brand_field_rep_id', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=True)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='field_reps', to='core.campaign')),
            ],
            options={'unique_together': {('campaign', 'email'), ('campaign', 'phone_number'), ('campaign', 'brand_field_rep_id')}},
        ),
        migrations.CreateModel(
            name='InClinicConfiguration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('in_charge_name', models.CharField(max_length=255)),
                ('in_charge_designation', models.CharField(max_length=255)),
                ('items_per_clinic_per_year', models.PositiveIntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('contract_file', models.FileField(blank=True, upload_to='contracts/')),
                ('brand_logo', models.URLField(blank=True)),
                ('company_logo', models.URLField(blank=True)),
                ('printing_required', models.BooleanField(default=False)),
                ('description', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('active', 'Active')], default='draft', max_length=10)),
                ('campaign_system', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='inclinic_config', to='core.campaignsystem')),
            ],
        ),
        migrations.CreateModel(
            name='Collateral',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cycle_label', models.CharField(default='default', max_length=50)),
                ('purpose', models.CharField(choices=[('doctor_long', 'Doctor Education Long'), ('doctor_short', 'Doctor Education Short'), ('patient_long', 'Patient Education Long'), ('patient_short', 'Patient Education Short')], max_length=30)),
                ('content_title', models.CharField(max_length=255)),
                ('content_id', models.CharField(blank=True, max_length=100)),
                ('item_type', models.CharField(choices=[('pdf', 'PDF'), ('video', 'Video'), ('both', 'PDF + Video')], max_length=10)),
                ('pdf_file', models.FileField(blank=True, upload_to='collaterals/pdf/')),
                ('vimeo_url', models.URLField(blank=True)),
                ('banner1', models.URLField(blank=True)),
                ('banner2', models.URLField(blank=True)),
                ('doctor_attribution', models.CharField(max_length=255)),
                ('content_description', models.TextField(blank=True)),
                ('webinar_link', models.URLField(blank=True)),
                ('webinar_title', models.CharField(blank=True, max_length=255)),
                ('webinar_description', models.TextField(blank=True)),
                ('webinar_date', models.DateField(blank=True, null=True)),
                ('whatsapp_template', models.TextField(help_text='Supports placeholder $collateralLinks')),
                ('sort_order', models.PositiveIntegerField(default=1)),
                ('campaign_system', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='collaterals', to='core.campaignsystem')),
            ],
        ),
    ]
