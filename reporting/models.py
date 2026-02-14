from django.db import models


class ActivityEventReport(models.Model):
    source_event_id = models.BigIntegerField(unique=True)
    campaign_id = models.BigIntegerField()
    cycle_id = models.BigIntegerField()
    field_rep_id = models.BigIntegerField()
    doctor_id = models.BigIntegerField()
    event_type = models.CharField(max_length=30)
    value = models.FloatField(default=1)
    occurred_at = models.DateTimeField()

    class Meta:
        ordering = ["-occurred_at"]
