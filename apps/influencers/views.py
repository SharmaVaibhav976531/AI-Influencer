import time
import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from django.utils import timezone
from django.http import StreamingHttpResponse

from apps.influencers.models import Influencer
from apps.influencers.services import openrouter_service
from apps.classification.models import Classification, SearchCriteria
from .services import batch_process_nlp, openrouter_service
from .services.export_service import get_export_queryset, generate_csv_response, generate_excel_response
from .services.result_service import get_filtered_classifications
from .forms import ResultFilterForm
from django.core.paginator import Paginator
from .services.discovery_service import DiscoveryService


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
def ai_classification_stream_view(request):
    """
    Server-Sent Events (SSE) stream endpoint providing real-time AI classification progress,
    terminal logs, live statistics, stage indicators, and error reporting.
    """
    def event_stream():
        user = request.user
        
        total_nlp_processed = Influencer.objects.filter(upload__user=user, nlp_processed_at__isnull=False).count()
        total_classified = Classification.objects.filter(influencer__upload__user=user, status='COMPLETED').count()
        
        pending_influencers = list(Influencer.objects.filter(
            upload__user=user,
            nlp_processed_at__isnull=False
        ).exclude(
            classifications__status='COMPLETED'
        ).distinct())
        
        pending_total = len(pending_influencers)
        
        # Terminal Header Banner
        logger.info("\n" + "=" * 57)
        logger.info("AI CLASSIFICATION STARTED")
        logger.info("=" * 57)
        logger.info(f"Total Influencers Found : {total_nlp_processed}")
        logger.info(f"Already Classified     : {total_classified}")
        logger.info(f"Pending                : {pending_total}")
        logger.info("-" * 57 + "\n")
        
        yield f"data: {json.dumps({'type': 'start', 'total_found': total_nlp_processed, 'already_classified': total_classified, 'pending_total': pending_total})}\n\n"
        
        if pending_total == 0:
            logger.info("=" * 57)
            logger.info("AI CLASSIFICATION COMPLETED")
            logger.info("=" * 57)
            logger.info("Total Records           : 0")
            logger.info("Successful              : 0")
            logger.info("Failed                  : 0")
            logger.info("Skipped                 : 0")
            logger.info("Total Time              : 00:00")
            logger.info("Average Time Per Record : 0.00 sec")
            logger.info("=" * 57 + "\n")
            yield f"data: {json.dumps({'type': 'complete', 'pending_total': 0, 'processed': 0, 'success': 0, 'failed': 0, 'total_time_str': '00:00', 'avg_time_seconds': 0.0, 'total_retries': 0})}\n\n"
            return

        criteria = SearchCriteria.objects.filter(user=user, status='ACTIVE').first()
        
        start_batch_time = time.time()
        processed_count = 0
        success_count = 0
        failed_count = 0
        total_retry_count = 0
        
        for idx, inf in enumerate(pending_influencers, 1):
            item_start_time = time.time()
            logger.info(f"[{idx}/{pending_total}]")
            logger.info(f"Handle: {inf.handle}")
            logger.info("Starting AI Classification...")
            
            stage_updates = []
            
            def stage_callback(stage_name, details=None):
                nonlocal total_retry_count
                if stage_name == "Retry":
                    total_retry_count += 1
                
                update_event = {
                    'type': 'stage_update',
                    'index': idx,
                    'pending_total': pending_total,
                    'handle': inf.handle,
                    'stage': stage_name,
                    'processed': processed_count,
                    'success': success_count,
                    'failed': failed_count,
                    'remaining': pending_total - processed_count,
                    'details': details
                }
                stage_updates.append(update_event)
                
            try:
                result = openrouter_service.classify_influencer(inf, criteria, stage_callback=stage_callback)
                
                for stg_evt in stage_updates:
                    yield f"data: {json.dumps(stg_evt)}\n\n"
                stage_updates.clear()
                
                if stage_callback:
                    stage_callback("Saving Result")
                logger.info("✓ Database Updated")
                
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
                logger.info("✓ Classification Completed")
                
                item_duration = time.time() - item_start_time
                logger.info(f"Time Taken: {item_duration:.2f} sec\n")
                
                processed_count += 1
                success_count += 1
                
            except Exception as e:
                for stg_evt in stage_updates:
                    yield f"data: {json.dumps(stg_evt)}\n\n"
                stage_updates.clear()
                
                item_duration = time.time() - item_start_time
                err_msg = str(e)
                logger.error(f"FAILED\nReason: {err_msg}")
                
                Classification.objects.create(
                    influencer=inf,
                    search_criteria=criteria,
                    status='FAILED',
                    reason=err_msg
                )
                
                processed_count += 1
                failed_count += 1
                logger.info(f"Time Taken: {item_duration:.2f} sec\n")
                
            remaining = pending_total - processed_count
            completion_pct = round((processed_count / pending_total) * 100, 2)
            
            logger.info("Progress")
            logger.info(f"Processed : {processed_count} / {pending_total}")
            logger.info(f"Success   : {success_count}")
            logger.info(f"Failed    : {failed_count}")
            logger.info(f"Remaining : {remaining}")
            logger.info(f"Completion: {completion_pct}%")
            logger.info("-" * 57 + "\n")
            
            item_event = {
                'type': 'item_complete',
                'index': idx,
                'pending_total': pending_total,
                'handle': inf.handle,
                'processed': processed_count,
                'success': success_count,
                'failed': failed_count,
                'remaining': remaining,
                'completion_pct': completion_pct,
                'item_duration': round(item_duration, 2),
                'total_retries': total_retry_count
            }
            yield f"data: {json.dumps(item_event)}\n\n"

        total_batch_time = time.time() - start_batch_time
        avg_time = round(total_batch_time / pending_total, 2) if pending_total > 0 else 0
        mins, secs = divmod(int(total_batch_time), 60)
        formatted_total_time = f"{mins:02d}:{secs:02d}"
        
        logger.info("=" * 57)
        logger.info("AI CLASSIFICATION COMPLETED")
        logger.info("=" * 57)
        logger.info(f"Total Records           : {pending_total}")
        logger.info(f"Successful              : {success_count}")
        logger.info(f"Failed                  : {failed_count}")
        logger.info(f"Skipped                 : 0")
        logger.info(f"Total Time              : {formatted_total_time} ({total_batch_time:.2f}s)")
        logger.info(f"Average Time Per Record : {avg_time:.2f} sec")
        logger.info("=" * 57 + "\n")
        
        final_event = {
            'type': 'complete',
            'pending_total': pending_total,
            'processed': processed_count,
            'success': success_count,
            'failed': failed_count,
            'total_time_str': formatted_total_time,
            'total_time_seconds': round(total_batch_time, 2),
            'avg_time_seconds': avg_time,
            'total_retries': total_retry_count
        }
        yield f"data: {json.dumps(final_event)}\n\n"

    response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


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


@login_required
def discovery_view(request):
    if request.method == 'POST':
        criteria = {
            'keywords': request.POST.get('keywords', ''),
            'platform': request.POST.get('platform', 'INSTAGRAM'),
            'language': request.POST.get('language', ''),
            'min_followers': request.POST.get('min_followers', 0),
            'max_results': int(request.POST.get('max_results', 5))
        }
        
        try:
            messages.info(request, "Starting real-time discovery and processing. This may take a moment...")
            result = DiscoveryService.execute(request.user, criteria)
            
            if result['processed'] > 0:
                messages.success(
                    request, 
                    f"Discovery complete! Found {result['discovered']} new influencers. "
                    f"Successfully processed {result['processed']} through NLP and AI. "
                    f"Skipped {result['skipped']} duplicates."
                )
            else:
                messages.warning(request, "No new influencers were discovered or all were duplicates.")
                
        except Exception as e:
            logger.error(f"Discovery failed: {str(e)}")
            messages.error(request, f"Discovery failed: {str(e)}")
            
        return redirect('influencers:results_list')
        
    return render(request, 'influencers/discovery.html')

