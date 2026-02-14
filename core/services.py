"""Service helpers for publisher flow."""

from .models import Campaign, SystemType


def has_inclinic_enabled(campaign: Campaign) -> bool:
    return campaign.systems.filter(system_type=SystemType.INCLINIC, is_enabled=True).exists()
