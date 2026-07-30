import pandas as pd
import logging
from django.core.exceptions import ValidationError

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