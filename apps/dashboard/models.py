from django.db import models
from utils.models import TimeStampedModel

class AnalyticsSnapshot(TimeStampedModel):
    total_uploads = models.IntegerField(default=0)
    total_influencers = models.IntegerField(default=0)
    relevant_influencers = models.IntegerField(default=0)
    average_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    top_platform = models.CharField(max_length=50, blank=True)
    top_language = models.CharField(max_length=100, blank=True)
    snapshot_date = models.DateField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-snapshot_date']
        verbose_name_plural = "Analytics Snapshots"

    def __str__(self) -> str:
        return f"Analytics Snapshot - {self.snapshot_date}"