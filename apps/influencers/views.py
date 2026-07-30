import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from django.utils import timezone

from apps.influencers.models import Influencer
from apps.influencers.services import openrouter_service
from apps.classification.models import Classification, SearchCriteria
from .services import batch_process_nlp, openrouter_service
from .services.export_service import get_export_queryset, generate_csv_response, generate_excel_response
from .services.result_service import get_filtered_classifications
from .forms import ResultFilterForm
from django.core.paginator import Paginator

logger = logging.getLogger(__name__)

@login_required
def nlp_processing_view(request):
    if request.method == "POST":
        messages.info(request, "Starting NLP processing. This may take a moment...")
        processed_count = batch_process_nlp(user=request.user)
        messages.success(request, f"Successfully processed {processed_count} influencers.")
        return redirect('influencers:nlp_dashboard')
    
    total_influencers = Influencer.objects.filter(upload__user=request.user).count()
    processed_influencers = Influencer.objects.filter(upload__user=request.user, nlp_processed_at__isnull=False).count()
    pending_count = total_influencers - processed_influencers
    
    avg_score = Influencer.objects.filter(
        upload__user=request.user, nlp_processed_at__isnull=False
    ).aggregate(Avg('rule_based_score'))['rule_based_score__avg'] or 0
    
    context = {
        'total_influencers': total_influencers,
        'processed_influencers': processed_influencers,
        'pending_count': pending_count,
        'avg_score': round(avg_score, 2) if avg_score else 0,
    }
    return render(request, 'influencers/nlp_dashboard.html', context)


@login_required
def ai_classification_view(request):
    if request.method == "POST":
        messages.info(request, "Starting AI Classification. This may take a few minutes...")
        
        # Fetch influencers with NLP data but no COMPLETED classification
        influencers = Influencer.objects.filter(
            upload__user=request.user,
            nlp_processed_at__isnull=False
        ).exclude(
            classifications__status='COMPLETED'
        ).distinct()
        
        # Use the user's first active search criteria, or None for default
        criteria = SearchCriteria.objects.filter(user=request.user, status='ACTIVE').first()
        
        processed_count = 0
        failed_count = 0
        
        for inf in influencers.iterator():
            try:
                result = openrouter_service.classify_influencer(inf, criteria)
                
                # Map AI recommendation string to Django Choice
                ai_rec = result.get('recommendation', 'Maybe').upper().replace(' ', '_')
                if ai_rec not in ['RECOMMEND', 'MAYBE', 'REJECT']:
                    ai_rec = 'MAYBE'
                
                Classification.objects.create(
                    influencer=inf,
                    search_criteria=criteria,
                    overall_score=result.get('overall_score', 0),
                    confidence_score=result.get('confidence_score', 0),
                    language_match=(result.get('language') == inf.language_detected),
                    orientation_match=(result.get('orientation') == 'Supportive'),
                    niche_match=True, 
                    keyword_match=len(result.get('matched_keywords', [])) > 0,
                    matched_keywords=result.get('matched_keywords', []),
                    reason=result.get('reason', ''),
                    recommendation=ai_rec,
                    ai_response=result,
                    status='COMPLETED',
                    ai_model_name=result.get('ai_model_name', ''),
                    processing_time_seconds=result.get('processing_time_seconds', 0),
                    summary=result.get('summary', '')
                )
                processed_count += 1
            except Exception as e:
                logger.error(f"Failed to classify {inf.handle}: {e}")
                Classification.objects.create(
                    influencer=inf,
                    search_criteria=criteria,
                    status='FAILED',
                    reason=str(e)
                )
                failed_count += 1
                
        messages.success(request, f"AI Classification completed. Processed: {processed_count}, Failed: {failed_count}.")
        return redirect('influencers:ai_classification')
        
    total_nlp_processed = Influencer.objects.filter(upload__user=request.user, nlp_processed_at__isnull=False).count()
    total_classified = Classification.objects.filter(influencer__upload__user=request.user, status='COMPLETED').count()
    pending_count = total_nlp_processed - total_classified
    
    context = {
        'total_nlp_processed': total_nlp_processed,
        'total_classified': total_classified,
        'pending_count': pending_count,
    }
    return render(request, 'influencers/ai_classification.html', context)


@login_required
def results_list_view(request):
    form = ResultFilterForm(request.GET)
    
    if form.is_valid():
        queryset = get_filtered_classifications(request.user, request.GET)
    else:
        queryset = get_filtered_classifications(request.user, {})
        
    paginator = Paginator(queryset, 25) # 25 results per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
    }
    return render(request, 'results/list.html', context)


@login_required
def influencer_detail_view(request, pk):
    # Optimize query: get influencer, its upload, and prefetch its classifications
    influencer = get_object_or_404(
        Influencer.objects.select_related('upload').prefetch_related('classifications'),
        pk=pk,
        upload__user=request.user
    )
    
    # Get the latest completed classification for this influencer
    classification = influencer.classifications.filter(status='COMPLETED').first()
    
    if not classification:
        messages.warning(request, "No completed AI classification found for this influencer.")
        return redirect('influencers:results_list')
        
    context = {
        'influencer': influencer,
        'classification': classification,
    }
    return render(request, 'results/detail.html', context)


@login_required
def export_results_view(request):
    """Handles exporting influencer results to CSV or Excel."""
    if request.method != 'POST':
        return redirect('influencers:results_list')
        
    export_format = request.POST.get('format', 'csv')
    export_type = request.POST.get('export_type', 'filtered') # 'selected', 'filtered', 'all'
    
    try:
        queryset = get_export_queryset(request, export_type)
        
        if not queryset.exists():
            messages.warning(request, "No records found to export.")
            return redirect('influencers:results_list')
            
        # Generate filename
        timestamp = timezone.now().strftime("%Y%m%d_%H%M")
        base_name = "influencer_results"
        
        # Add context to filename if filtered
        platform = request.GET.get('platform', '')
        if platform:
            base_name += f"_{platform.lower()}"
            
        if export_format == 'excel':
            filename = f"{base_name}_{timestamp}.xlsx"
            response = generate_excel_response(queryset, filename)
        else:
            filename = f"{base_name}_{timestamp}.csv"
            response = generate_csv_response(queryset, filename)
            
        logger.info(f"User {request.user.username} exported {queryset.count()} records as {export_format.upper()}")
        return response
        
    except Exception as e:
        logger.error(f"Export failed for user {request.user.username}: {str(e)}")
        messages.error(request, "An error occurred while generating the export. Please try again.")
        return redirect('influencers:results_list')