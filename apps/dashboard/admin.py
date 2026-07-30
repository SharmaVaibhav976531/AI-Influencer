from django.contrib import admin
from .models import AnalyticsSnapshot

@admin.register(AnalyticsSnapshot)
class AnalyticsSnapshotAdmin(admin.ModelAdmin):
    list_display = ('snapshot_date', 'total_uploads', 'total_influencers', 'relevant_influencers', 'average_score')
    list_filter = ('snapshot_date',)
    ordering = ('-snapshot_date',)
    readonly_fields = ('snapshot_date', 'created_at', 'updated_at')