from django.contrib import admin
from .models import Upload

@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'user', 'file_type', 'status', 'total_rows', 'created_at')
    list_filter = ('status', 'file_type', 'created_at')
    search_fields = ('original_filename', 'user__username')
    readonly_fields = ('created_at', 'updated_at')