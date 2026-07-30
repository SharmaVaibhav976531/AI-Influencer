from django.contrib import admin
from .models import Influencer

@admin.register(Influencer)
class InfluencerAdmin(admin.ModelAdmin):
    list_display = ('name', 'handle', 'platform', 'followers', 'language', 'is_active', 'created_at')
    list_filter = ('platform', 'language', 'is_active', 'created_at')
    search_fields = ('name', 'handle', 'bio', 'location')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'raw_data')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'handle', 'platform', 'profile_url')
        }),
        ('Metrics', {
            'fields': ('followers', 'following', 'total_posts')
        }),
        ('Details', {
            'fields': ('bio', 'description', 'language', 'location', 'email', 'website')
        }),
        ('System', {
            'fields': ('upload', 'is_active', 'raw_data', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )