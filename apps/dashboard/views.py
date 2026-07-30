from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.uploads.models import Upload
from apps.influencers.models import Influencer
from .services.analytics_service import get_analytics_context

@login_required
def home_view(request):
    user_uploads = Upload.objects.filter(user=request.user)
    
    total_uploads = user_uploads.count()
    total_rows = sum(upload.total_rows for upload in user_uploads.filter(status=Upload.Status.SUCCESS))
    successful_uploads = user_uploads.filter(status=Upload.Status.SUCCESS).count()
    failed_uploads = user_uploads.filter(status=Upload.Status.FAILED).count()
    
    nlp_processed_count = Influencer.objects.filter(upload__user=request.user, nlp_processed_at__isnull=False).count()
    from apps.classification.models import Classification
    ai_classified_count = Classification.objects.filter(influencer__upload__user=request.user, status='COMPLETED').count()
    
    recent_uploads = user_uploads.order_by('-created_at')[:5]

    context = {
        'page_title': 'Dashboard Overview',
        'total_uploads': total_uploads,
        'total_rows': total_rows,
        'successful_uploads': successful_uploads,
        'failed_uploads': failed_uploads,
        'nlp_processed_count': nlp_processed_count,
        'ai_classified_count': ai_classified_count,
        'recent_uploads': recent_uploads,
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def analytics_dashboard_view(request):
    filters = {
        'date_range': request.GET.get('date_range'),
        'custom_start': request.GET.get('custom_start'),
        'custom_end': request.GET.get('custom_end'),
        'platform': request.GET.get('platform'),
        'language': request.GET.get('language'),
        'recommendation': request.GET.get('recommendation'),
        'min_score': request.GET.get('min_score'),
        'max_score': request.GET.get('max_score'),
    }
    
    context = get_analytics_context(request.user, filters)
    return render(request, 'analytics/dashboard.html', context)
