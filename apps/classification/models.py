from django.db import models
from django.conf import settings
from utils.models import TimeStampedModel

class SearchCriteria(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'

    class Orientation(models.TextChoices):
        SUPPORTIVE = 'SUPPORTIVE', 'Supportive'
        NEUTRAL = 'NEUTRAL', 'Neutral'
        OPPOSED = 'OPPOSED', 'Opposed'
        UNKNOWN = 'UNKNOWN', 'Unknown'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='search_criteria'
    )
    name = models.CharField(max_length=255)
    keywords = models.JSONField(default=list, blank=True)
    languages = models.JSONField(default=list, blank=True)
    orientation = models.CharField(
        max_length=20, 
        choices=Orientation.choices, 
        blank=True, 
        null=True
    )
    niches = models.JSONField(default=list, blank=True)
    minimum_followers = models.BigIntegerField(default=0)
    platforms = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.name} ({self.user.username})"


class Classification(TimeStampedModel):
    class Recommendation(models.TextChoices):
        RECOMMEND = 'RECOMMEND', 'Recommend'
        MAYBE = 'MAYBE', 'Maybe'
        REJECT = 'REJECT', 'Reject'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    influencer = models.ForeignKey(
        'influencers.Influencer', 
        on_delete=models.CASCADE, 
        related_name='classifications'
    )
    search_criteria = models.ForeignKey(
        SearchCriteria, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='classifications'
    )
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    language_match = models.BooleanField(default=False)
    orientation_match = models.BooleanField(default=False)
    niche_match = models.BooleanField(default=False)
    keyword_match = models.BooleanField(default=False)
    matched_keywords = models.JSONField(default=list, blank=True)
    reason = models.TextField(blank=True)
    recommendation = models.CharField(
        max_length=20, 
        choices=Recommendation.choices, 
        default=Recommendation.MAYBE
    )
    ai_response = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['influencer', 'search_criteria']),
            models.Index(fields=['status']),
        ]

    def __str__(self) -> str:
        return f"Classification for {self.influencer.handle} (Score: {self.overall_score}%)"