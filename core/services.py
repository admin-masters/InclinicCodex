from django.utils import timezone
from .models import CampaignCycle


def get_current_cycle(campaign):
    today = timezone.now().date()
    return campaign.cycles.filter(start_date__lte=today, end_date__gte=today).order_by("cycle_number").first()


def get_active_collaterals(campaign):
    current = get_current_cycle(campaign)
    if not current:
        return campaign.cycles.none()
    return CampaignCycle.objects.filter(campaign=campaign, cycle_number__lte=current.cycle_number).order_by("cycle_number")
