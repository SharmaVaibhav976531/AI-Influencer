# apps/uploads/services.py
import time
import logging
import pandas as pd
from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Upload
from .utils import normalize_headers, parse_followers, clean_text, normalize_platform
from apps.influencers.models import Influencer 

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    'name', 'handle', 'platform', 'followers', 'bio', 
    'description', 'posts', 'language', 'location', 'profile_url'
]

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

def validate_file(file):
    """Validates file extension, size, and basic properties before saving."""
    if file.size > MAX_FILE_SIZE_BYTES:
        raise ValidationError(f"File size exceeds the maximum limit of {MAX_FILE_SIZE_MB}MB.")
    
    ext = file.name.split('.')[-1].lower()
    if ext not in ['csv', 'xlsx']:
        raise ValidationError("Unsupported file format. Only CSV and XLSX are allowed.")
    
    if file.size == 0:
        raise ValidationError("The uploaded file is empty.")


def parse_and_validate_data(file_path: str, file_type: str) -> tuple[pd.DataFrame, int]:
    """
    Parses the file using pandas and validates required columns.
    Returns the dataframe and total row count.
    """
    try:
        if file_type == 'CSV':
            df = pd.read_csv(file_path, encoding='utf-8')
        else:
            df = pd.read_excel(file_path, engine='openpyxl')
    except UnicodeDecodeError:
        raise ValidationError("Invalid file encoding. Please ensure the CSV is UTF-8 encoded.")
    except Exception as e:
        logger.error(f"Error parsing file {file_path}: {str(e)}")
        raise ValidationError(f"Failed to parse file. It might be corrupted or invalid. Error: {str(e)}")

    if df.empty:
        raise ValidationError("The uploaded file contains no data rows.")

    # Normalize column names for checking (lowercase, strip spaces, replace spaces with underscores)
    df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
    
    # Check required columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValidationError(f"Missing required columns: {', '.join(missing_cols)}.")

    return df, len(df)

@transaction.atomic
def process_upload_file(upload_id: int) -> None:
    """
    Complete ETL pipeline for processing an uploaded file.
    Reads, cleans, validates, saves preview, and bulk-inserts influencer data.
    """
    # Lock the row to prevent concurrent processing
    upload = Upload.objects.select_for_update().get(pk=upload_id)
    
    # Update processing status
    upload.processing_status = Upload.ProcessingStatus.PROCESSING
    upload.save(update_fields=['processing_status'])
    
    start_time = time.time()
    total_rows = 0
    invalid_count = 0
    influencers_to_create = []
    
    try:
        # 1. Read File
        if upload.file_type == Upload.FileType.CSV:
            df = pd.read_csv(upload.file.path, encoding='utf-8')
        else:
            df = pd.read_excel(upload.file.path, engine='openpyxl')
            
        # 2. Normalize Headers
        df = normalize_headers(df)
        total_rows = len(df)
        
        if total_rows == 0:
            raise ValidationError("The uploaded file contains no data rows.")
            
        # 3. Validate Required Columns
        required_cols = ['name', 'handle', 'platform']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValidationError(f"Missing required columns: {', '.join(missing_cols)}")
            
        # 4. Save Preview Data (First 10 rows) for the UI
        preview_df = df.head(10)
        preview_df = preview_df.where(pd.notnull(preview_df), None) # Replace NaN with None for JSON
        upload.preview_data = preview_df.to_dict(orient='records')
            
        # 5. Iterate and Clean Data
        for _, row in df.iterrows():
            try:
                name = clean_text(row.get('name'))
                handle = clean_text(row.get('handle'))
                platform = normalize_platform(row.get('platform'))
                
                # Validate required fields
                if not name or not handle:
                    invalid_count += 1
                    continue
                    
                # Parse and clean optional fields
                followers = parse_followers(row.get('followers', 0))
                following = parse_followers(row.get('following', 0))
                posts = parse_followers(row.get('posts', 0))
                
                # Create Influencer instance (not saved to DB yet)
                inf = Influencer(
                    upload=upload,
                    name=name,
                    handle=handle,
                    platform=platform,
                    followers=followers,
                    following=following,
                    total_posts=posts,
                    bio=clean_text(row.get('bio')),
                    description=clean_text(row.get('description')),
                    language=clean_text(row.get('language')),
                    location=clean_text(row.get('location')),
                    profile_url=clean_text(row.get('profile_url')),
                    email=clean_text(row.get('email')),
                    website=clean_text(row.get('website')),
                    raw_data={k: str(v) for k, v in row.to_dict().items() if pd.notna(v)}
                )
                influencers_to_create.append(inf)
                
            except Exception as e:
                logger.warning(f"Invalid row skipped during processing: {e}")
                invalid_count += 1
                
        # 6. Bulk Insert (ignore_conflicts handles duplicates gracefully via DB constraint)
        valid_count = len(influencers_to_create)
        Influencer.objects.bulk_create(
            influencers_to_create, 
            ignore_conflicts=True, 
            batch_size=1000
        )
        
        # 7. Calculate Exact Imported vs Duplicate Counts
        imported_count = Influencer.objects.filter(upload=upload).count()
        duplicate_count = valid_count - imported_count
        
        processing_time = time.time() - start_time
        
        # 8. Update Upload Status and Summary
        upload.processing_status = Upload.ProcessingStatus.COMPLETED
        upload.total_rows = total_rows
        upload.processing_summary = {
            'total_rows': total_rows,
            'imported': imported_count,
            'duplicates': duplicate_count,
            'invalid': invalid_count,
            'processing_time_seconds': round(processing_time, 2)
        }
        upload.save(update_fields=['processing_status', 'total_rows', 'processing_summary', 'preview_data'])
        
        logger.info(
            f"Upload {upload_id} processed successfully. "
            f"Total: {total_rows}, Imported: {imported_count}, "
            f"Duplicates: {duplicate_count}, Invalid: {invalid_count}"
        )
        
    except Exception as e:
        logger.error(f"Upload {upload_id} failed: {str(e)}")
        upload.processing_status = Upload.ProcessingStatus.FAILED
        upload.error_message = str(e)
        upload.save(update_fields=['processing_status', 'error_message'])
        
        # Clean up the physical file on failure to save space
        if upload.file and os.path.isfile(upload.file.path):
            os.remove(upload.file.path)
            
        raise