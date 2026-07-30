from django.contrib import admin
from .models import SearchCriteria, Classification

@admin.register(SearchCriteria)
class SearchCriteriaAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'status', 'minimum_followers', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Classification)
class ClassificationAdmin(admin.ModelAdmin):
    list_display = ('influencer', 'search_criteria', 'overall_score', 'recommendation', 'status', 'created_at')
    list_filter = ('status', 'recommendation', 'language_match', 'created_at')
    search_fields = ('influencer__handle', 'influencer__name', 'reason')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'ai_response')
    fieldsets = (
        ('Matching Details', {
            'fields': ('influencer', 'search_criteria', 'status')
        }),
        ('Scores & Matches', {
            'fields': ('overall_score', 'confidence_score', 'language_match', 'orientation_match', 'niche_match', 'keyword_match', 'matched_keywords')
        }),
        ('AI Output', {
            'fields': ('reason', 'recommendation', 'ai_response'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('created_at', 'updated_at')
        })
    )