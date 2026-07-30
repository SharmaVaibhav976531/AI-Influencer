# apps/uploads/views.py
import os
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .forms import UploadFileForm
from .models import Upload
from .services import process_upload_file

logger = logging.getLogger(__name__)

@login_required
def upload_view(request):
    """Handles file upload and triggers the ETL processing pipeline."""
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            ext = file.name.split('.')[-1].lower()
            file_type = Upload.FileType.CSV if ext == 'csv' else Upload.FileType.XLSX
            
            # 1. Create Upload record initially as PENDING
            upload = Upload.objects.create(
                user=request.user,
                file=file,
                original_filename=file.name,
                file_type=file_type,
                file_size=file.size,
                status=Upload.Status.SUCCESS,  # File saved to disk successfully
                processing_status=Upload.ProcessingStatus.PENDING
            )
            
            try:
                # 2. Trigger the ETL processing pipeline (reads, cleans, validates, bulk inserts)
                process_upload_file(upload.pk)
                messages.success(request, f"File '{file.name}' processed successfully!")
                return redirect('uploads:preview', pk=upload.pk)
                
            except Exception as e:
                messages.error(request, f"Processing failed: {str(e)}")
                return redirect('uploads:upload')
    else:
        form = UploadFileForm()
        
    return render(request, 'uploads/upload.html', {'form': form})


@login_required
def upload_history_view(request):
    """Displays paginated, searchable, and filterable upload history."""
    queryset = Upload.objects.filter(user=request.user).order_by('-created_at')
    
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(original_filename__icontains=search_query)
        
    file_type = request.GET.get('file_type', '')
    if file_type and file_type in Upload.FileType.values:
        queryset = queryset.filter(file_type=file_type)
        
    status = request.GET.get('status', '')
    if status and status in Upload.Status.values:
        queryset = queryset.filter(status=status)
        
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'file_type': file_type,
        'status': status,
        'file_types': Upload.FileType.choices,
        'statuses': Upload.Status.choices,
    }
    return render(request, 'uploads/history.html', context)


@login_required
def upload_preview_view(request, pk):
    """Displays detailed metadata and the 10-row data preview for a specific upload."""
    upload = get_object_or_404(Upload, pk=pk, user=request.user)
    
    context = {
        'upload': upload,
    }
    return render(request, 'uploads/preview.html', context)