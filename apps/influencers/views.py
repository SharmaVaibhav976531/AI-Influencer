from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .models import Influencer
from .services import batch_process_nlp

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