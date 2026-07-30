from django.db import models
from django.conf import settings
from utils.models import TimeStampedModel

class ActiveInfluencerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class Influencer(TimeStampedModel):
    class Platform(models.TextChoices):
        INSTAGRAM = 'INSTAGRAM', 'Instagram'
        YOUTUBE = 'YOUTUBE', 'YouTube'
        TWITTER = 'TWITTER', 'Twitter'
        FACEBOOK = 'FACEBOOK', 'Facebook'
        LINKEDIN = 'LINKEDIN', 'LinkedIn'
        OTHER = 'OTHER', 'Other'

    upload = models.ForeignKey(
        'uploads.Upload', 
        on_delete=models.CASCADE, 
        related_name='influencers'
    )
    name = models.CharField(max_length=255)
    handle = models.CharField(max_length=255, db_index=True)
    platform = models.CharField(max_length=20, choices=Platform.choices, db_index=True)
    followers = models.BigIntegerField(default=0, db_index=True)
    following = models.BigIntegerField(default=0)
    total_posts = models.BigIntegerField(default=0)
    bio = models.TextField(blank=True)
    description = models.TextField(blank=True)
    language = models.CharField(max_length=100, blank=True, db_index=True)
    location = models.CharField(max_length=255, blank=True)
    profile_url = models.URLField(max_length=500, blank=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    raw_data = models.JSONField(default=dict, blank=True)

    objects = models.Manager()
    active_objects = ActiveInfluencerManager()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['handle']),
            models.Index(fields=['platform']),
            models.Index(fields=['language']),
            models.Index(fields=['followers']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['handle', 'platform'], 
                name='unique_influencer_handle_platform'
            ),
            models.CheckConstraint(
                condition=models.Q(followers__gte=0),
                name='followers_non_negative'
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} (@{self.handle}) - {self.platform}"