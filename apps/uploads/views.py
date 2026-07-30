import os
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .forms import UploadFileForm
from .models import Upload
from .services import parse_and_validate_data

logger = logging.getLogger(__name__)

@login_required
def upload_view(request):
    """Handles file upload, validation, parsing, and preview generation."""
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            
            ext = file.name.split('.')[-1].lower()
            file_type = Upload.FileType.CSV if ext == 'csv' else Upload.FileType.XLSX
            
            # Create Upload record initially as PENDING
            upload = Upload.objects.create(
                user=request.user,
                file=file,
                original_filename=file.name,
                file_type=file_type,
                file_size=file.size,
                status=Upload.Status.PENDING
            )
            
            try:
                file_path = upload.file.path
                df, total_rows = parse_and_validate_data(file_path, file_type)
                
                # Update upload record with success data
                upload.total_rows = total_rows
                upload.status = Upload.Status.SUCCESS
                
                # Save preview data (first 10 rows)
                preview_df = df.head(10)
                preview_df = preview_df.where(pd.notnull(preview_df), None) # Replace NaN with None for JSON
                upload.preview_data = preview_df.to_dict(orient='records')
                
                upload.save()
                
                messages.success(request, f"File '{file.name}' uploaded and processed successfully!")
                return redirect('uploads:preview', pk=upload.pk)
                
            except Exception as e:
                # If parsing fails, mark as FAILED
                upload.status = Upload.Status.FAILED
                upload.error_message = str(e)
                upload.save()
                
                # Delete the physical file to save space
                if upload.file and os.path.isfile(upload.file.path):
                    os.remove(upload.file.path)
                    
                messages.error(request, f"Upload failed: {str(e)}")
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