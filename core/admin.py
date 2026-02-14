from django.contrib import admin
from .models import Campaign, CampaignCycle, FieldRepresentative, Doctor, ShareRecord, ActivityEvent

admin.site.register([Campaign, CampaignCycle, FieldRepresentative, Doctor, ShareRecord, ActivityEvent])
