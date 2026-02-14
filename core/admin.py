from django.contrib import admin
from .models import Campaign, CampaignSystem, InClinicConfiguration, FieldRepresentative, FieldRepRecruitmentLink, Collateral

admin.site.register(Campaign)
admin.site.register(CampaignSystem)
admin.site.register(InClinicConfiguration)
admin.site.register(FieldRepresentative)
admin.site.register(FieldRepRecruitmentLink)
admin.site.register(Collateral)
