from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import ActivityEvent
from reporting.models import ActivityEventReport


class Command(BaseCommand):
    help = "Move activity events from transaction DB to reporting DB"

    def handle(self, *args, **options):
        events = list(ActivityEvent.objects.using("default").all())
        moved = 0
        for event in events:
            with transaction.atomic(using="reporting"):
                ActivityEventReport.objects.using("reporting").get_or_create(
                    source_event_id=event.id,
                    defaults={
                        "campaign_id": event.share.campaign_id,
                        "cycle_id": event.share.cycle_id,
                        "field_rep_id": event.share.field_rep_id,
                        "doctor_id": event.doctor_id,
                        "event_type": event.event_type,
                        "value": event.value,
                        "occurred_at": event.created_at,
                    },
                )
            moved += 1
        ActivityEvent.objects.using("default").all().delete()
        self.stdout.write(self.style.SUCCESS(f"Moved {moved} events to reporting database."))
