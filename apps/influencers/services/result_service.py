# apps/influencers/services/result_service.py

from django.db.models import Q
from django.core.paginator import Paginator
from apps.classification.models import Classification

SORT_MAPPING = {
    'score': '-overall_score',
    'score_asc': 'overall_score',
    'followers': '-influencer__followers',
    'followers_asc': 'influencer__followers',
    'name': 'influencer__name',
    'name_desc': '-influencer__name',
    'platform': 'influencer__platform',
    'date': '-influencer__created_at',
    'date_asc': 'influencer__created_at',
    'confidence': '-confidence_score',
}

def get_filtered_classifications(user, query_params):
    """
    Builds an optimized, filtered, sorted, and paginated queryset of classifications.
    """
    queryset = Classification.objects.filter(
        status='COMPLETED'
    ).filter(
        Q(influencer__upload__user=user) | Q(influencer__user=user)
    ).select_related('influencer', 'influencer__upload', 'influencer__user')

    # 1. Global Search
    search = query_params.get('search', '').strip()
    if search:
        queryset = queryset.filter(
            Q(influencer__name__icontains=search) |
            Q(influencer__handle__icontains=search) |
            Q(influencer__platform__icontains=search) |
            Q(influencer__language_detected__icontains=search) |
            Q(influencer__extracted_keywords__icontains=search) |
            Q(recommendation__icontains=search)
        )

    # 2. Advanced Filters
    platform = query_params.get('platform')
    if platform:
        queryset = queryset.filter(influencer__platform=platform)

    language = query_params.get('language')
    if language:
        queryset = queryset.filter(influencer__language_detected__icontains=language)

    recommendation = query_params.get('recommendation')
    if recommendation:
        queryset = queryset.filter(recommendation=recommendation)

    # NEW: Source Filter
    source = query_params.get('source')
    if source:
        queryset = queryset.filter(influencer__source=source)

    min_score = query_params.get('min_score')
    if min_score:
        queryset = queryset.filter(overall_score__gte=min_score)

    max_score = query_params.get('max_score')
    if max_score:
        queryset = queryset.filter(overall_score__lte=max_score)

    min_followers = query_params.get('min_followers')
    if min_followers:
        queryset = queryset.filter(influencer__followers__gte=min_followers)

    max_followers = query_params.get('max_followers')
    if max_followers:
        queryset = queryset.filter(influencer__followers__lte=max_followers)

    # 3. Sorting
    sort_by = query_params.get('sort', 'score')
    order_by = SORT_MAPPING.get(sort_by, '-overall_score')
    queryset = queryset.order_by(order_by)

    return queryset