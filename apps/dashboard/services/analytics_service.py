from django.db.models import Count, Avg, Sum, Min, Max, Q
from django.utils import timezone
from datetime import timedelta
from collections import Counter

from apps.uploads.models import Upload
from apps.influencers.models import Influencer
from apps.classification.models import Classification
from .chart_service import get_chart_data

def apply_date_filters(qs, date_field, date_range, custom_start, custom_end):
    now = timezone.now()
    if date_range == 'today':
        qs = qs.filter(**{f'{date_field}__date': now.date()})
    elif date_range == '7days':
        qs = qs.filter(**{f'{date_field}__gte': now - timedelta(days=7)})
    elif date_range == '30days':
        qs = qs.filter(**{f'{date_field}__gte': now - timedelta(days=30)})
    elif date_range == '90days':
        qs = qs.filter(**{f'{date_field}__gte': now - timedelta(days=90)})
    elif date_range == 'this_year':
        qs = qs.filter(**{f'{date_field}__year': now.year})
    elif date_range == 'custom' and custom_start and custom_end:
        qs = qs.filter(**{f'{date_field}__date__gte': custom_start, f'{date_field}__date__lte': custom_end})
    return qs

def get_filtered_querysets(user, filters):
    upload_qs = Upload.objects.filter(user=user)
    influencer_qs = Influencer.objects.filter(upload__user=user)
    classification_qs = Classification.objects.filter(influencer__upload__user=user, status='COMPLETED')
    
    # Date Filters
    date_range = filters.get('date_range')
    custom_start = filters.get('custom_start')
    custom_end = filters.get('custom_end')
    
    upload_qs = apply_date_filters(upload_qs, 'created_at', date_range, custom_start, custom_end)
    influencer_qs = apply_date_filters(influencer_qs, 'created_at', date_range, custom_start, custom_end)
    classification_qs = apply_date_filters(classification_qs, 'created_at', date_range, custom_start, custom_end)
    
    # Categorical Filters
    platform = filters.get('platform')
    if platform:
        influencer_qs = influencer_qs.filter(platform=platform)
        classification_qs = classification_qs.filter(influencer__platform=platform)
        
    language = filters.get('language')
    if language:
        influencer_qs = influencer_qs.filter(language_detected__icontains=language)
        classification_qs = classification_qs.filter(influencer__language_detected__icontains=language)
        
    recommendation = filters.get('recommendation')
    if recommendation:
        classification_qs = classification_qs.filter(recommendation=recommendation)
        
    # Numeric Filters
    min_score = filters.get('min_score')
    if min_score:
        classification_qs = classification_qs.filter(overall_score__gte=min_score)
        
    max_score = filters.get('max_score')
    if max_score:
        classification_qs = classification_qs.filter(overall_score__lte=max_score)
        
    return upload_qs, influencer_qs, classification_qs

def get_kpi_data(upload_qs, influencer_qs, classification_qs):
    return {
        'total_uploads': upload_qs.count(),
        'total_influencers': influencer_qs.count(),
        'total_classified': classification_qs.count(),
        'highly_relevant': classification_qs.filter(recommendation='RECOMMEND').count(),
        'moderately_relevant': classification_qs.filter(recommendation='MAYBE').count(),
        'low_match': classification_qs.filter(recommendation='REJECT').count(),
        'avg_score': classification_qs.aggregate(Avg('overall_score'))['overall_score__avg'] or 0,
        'avg_confidence': classification_qs.aggregate(Avg('confidence_score'))['confidence_score__avg'] or 0,
        'avg_rule_score': influencer_qs.aggregate(Avg('rule_based_score'))['rule_based_score__avg'] or 0,
    }

def get_summary_stats(influencer_qs, classification_qs):
    follower_stats = influencer_qs.aggregate(
        Avg('followers'), Max('followers'), Min('followers')
    )
    
    # Extract unique keywords and schemes using Python Counter for JSONFields
    keyword_counter = Counter()
    for inf in influencer_qs.only('extracted_keywords').iterator():
        keyword_counter.update(inf.extracted_keywords)
        
    scheme_counter = Counter()
    for c in classification_qs.only('ai_response').iterator():
        schemes = c.ai_response.get('government_scheme_mentions', [])
        scheme_counter.update(schemes)

    return {
        'total_platforms': influencer_qs.values('platform').distinct().count(),
        'total_languages': influencer_qs.values('language_detected').distinct().count(),
        'total_keywords': len(keyword_counter),
        'total_schemes': len(scheme_counter),
        'avg_followers': follower_stats['followers__avg'] or 0,
        'max_followers': follower_stats['followers__max'] or 0,
        'min_followers': follower_stats['followers__min'] or 0,
        'avg_rule_score': influencer_qs.aggregate(Avg('rule_based_score'))['rule_based_score__avg'] or 0,
    }

def get_top_lists(influencer_qs, classification_qs):
    # Top Platforms & Languages
    top_platforms = influencer_qs.values('platform').annotate(count=Count('id')).order_by('-count')[:5]
    top_languages = influencer_qs.values('language_detected').annotate(count=Count('id')).order_by('-count')[:5]
    
    # Top Keywords & Schemes
    keyword_counter = Counter()
    for inf in influencer_qs.only('extracted_keywords').iterator():
        keyword_counter.update(inf.extracted_keywords)
        
    scheme_counter = Counter()
    for c in classification_qs.only('ai_response').iterator():
        schemes = c.ai_response.get('government_scheme_mentions', [])
        scheme_counter.update(schemes)

    return {
        'platforms': top_platforms,
        'languages': top_languages,
        'keywords': keyword_counter.most_common(5),
        'schemes': scheme_counter.most_common(5),
    }

def get_recent_activity(upload_qs, classification_qs):
    return {
        'uploads': upload_qs.order_by('-created_at')[:5],
        'classifications': classification_qs.select_related('influencer').order_by('-created_at')[:5],
    }

def get_analytics_context(user, filters):
    upload_qs, influencer_qs, classification_qs = get_filtered_querysets(user, filters)
    
    context = {
        'kpi': get_kpi_data(upload_qs, influencer_qs, classification_qs),
        'summary': get_summary_stats(influencer_qs, classification_qs),
        'charts': get_chart_data(influencer_qs, classification_qs, upload_qs),
        'top_lists': get_top_lists(influencer_qs, classification_qs),
        'recent': get_recent_activity(upload_qs, classification_qs),
        'filters': filters,
        'platform_choices': Influencer.Platform.choices,
        'recommendation_choices': Classification.Recommendation.choices,
    }
    return context