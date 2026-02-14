from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ActivityEventReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_event_id', models.BigIntegerField(unique=True)),
                ('campaign_id', models.BigIntegerField()),
                ('cycle_id', models.BigIntegerField()),
                ('field_rep_id', models.BigIntegerField()),
                ('doctor_id', models.BigIntegerField()),
                ('event_type', models.CharField(max_length=30)),
                ('value', models.FloatField(default=1)),
                ('occurred_at', models.DateTimeField()),
            ],
            options={'ordering': ['-occurred_at']},
        )
    ]
