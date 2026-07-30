import os
from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator
from utils.models import TimeStampedModel

class Upload(TimeStampedModel):
    class FileType(models.TextChoices):
        CSV = 'CSV', 'CSV'
        XLSX = 'XLSX', 'Excel'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'
    
    class ProcessingStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='uploads'
    )
    file = models.FileField(
        upload_to='uploads/%Y/%m/%d/', 
        validators=[FileExtensionValidator(allowed_extensions=['csv', 'xlsx'])]
    )
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FileType.choices)
    file_size = models.BigIntegerField(help_text="File size in bytes")
    total_rows = models.IntegerField(default=0)
    status = models.CharField(
        max_length=10, 
        choices=Status.choices, 
        default=Status.PENDING
    )
    processing_status = models.CharField(
        max_length=10, 
        choices=ProcessingStatus.choices, 
        default=ProcessingStatus.PENDING
    )
    error_message = models.TextField(blank=True, null=True)
    preview_data = models.JSONField(default=list, blank=True, help_text="First 10 rows as JSON")
    

    def __str__(self):
        return f"{self.original_filename} - {self.user.username}"

    @property
    def file_size_mb(self):
        """Returns file size in MB rounded to 2 decimal places."""
        return round(self.file_size / (1024 * 1024), 2)
    
    def is_processed(self) -> bool:
        return self.processing_status == self.ProcessingStatus.COMPLETED