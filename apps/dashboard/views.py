from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.uploads.models import Upload

@login_required
def home_view(request):
    user_uploads = Upload.objects.filter(user=request.user)
    
    total_uploads = user_uploads.count()
    total_rows = sum(upload.total_rows for upload in user_uploads.filter(status=Upload.Status.SUCCESS))
    successful_uploads = user_uploads.filter(status=Upload.Status.SUCCESS).count()
    failed_uploads = user_uploads.filter(status=Upload.Status.FAILED).count()
    
    recent_uploads = user_uploads.order_by('-created_at')[:5]

    context = {
        'page_title': 'Dashboard Overview',
        'total_uploads': total_uploads,
        'total_rows': total_rows,
        'successful_uploads': successful_uploads,
        'failed_uploads': failed_uploads,
        'recent_uploads': recent_uploads,
    }
    return render(request, 'dashboard/home.html', context)