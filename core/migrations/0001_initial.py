from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('campaign_id', models.CharField(editable=False, max_length=32, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('brand_name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('banner_top_url', models.URLField(blank=True)),
                ('banner_top_target', models.URLField(blank=True)),
                ('banner_bottom_url', models.URLField(blank=True)),
                ('banner_bottom_target', models.URLField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Doctor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('whatsapp_number', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='CampaignCycle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cycle_number', models.PositiveIntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('title', models.CharField(max_length=255)),
                ('message_template', models.TextField()),
                ('reminder_template', models.TextField()),
                ('pdf_url', models.URLField()),
                ('video_vimeo_url', models.URLField()),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cycles', to='core.campaign')),
            ],
            options={'unique_together': {('campaign', 'cycle_number')}},
        ),
        migrations.CreateModel(
            name='FieldRepresentative',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('whatsapp_number', models.CharField(max_length=20)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='field_reps', to='core.campaign')),
            ],
        ),
        migrations.CreateModel(
            name='ShareRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(editable=False, max_length=64, unique=True)),
                ('whatsapp_message', models.TextField()),
                ('is_reminder', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('sent', 'Sent'), ('read', 'Read')], default='sent', max_length=10)),
                ('shared_at', models.DateTimeField(auto_now_add=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.campaign')),
                ('cycle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.campaigncycle')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.doctor')),
                ('field_rep', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.fieldrepresentative')),
            ],
        ),
        migrations.CreateModel(
            name='ActivityEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('whatsapp_click', 'WhatsApp Link Click'), ('landing_visit', 'Landing Visit'), ('pdf_last_page', 'PDF Last Page'), ('video_progress', 'Video Progress'), ('pdf_download', 'PDF Download')], max_length=30)),
                ('value', models.FloatField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.doctor')),
                ('share', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='core.sharerecord')),
            ],
        ),
    ]
