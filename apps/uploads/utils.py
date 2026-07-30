# apps/uploads/utils.py
import re
import pandas as pd
import numpy as np

# Mapping of common header variations to standard schema names
HEADER_MAPPING = {
    'follower count': 'followers', 'followers count': 'followers', 'followers': 'followers',
    'following count': 'following', 'followings': 'following', 'following': 'following',
    'posts': 'posts', 'total posts': 'posts', 'post count': 'posts',
    'profile url': 'profile_url', 'url': 'profile_url', 'link': 'profile_url', 'profile_link': 'profile_url',
    'name': 'name', 'fullname': 'name', 'full name': 'name',
    'handle': 'handle', 'username': 'handle', 'user name': 'handle',
    'platform': 'platform', 'source': 'platform', 'network': 'platform',
    'bio': 'bio', 'biography': 'bio',
    'description': 'description', 'desc': 'description',
    'language': 'language', 'lang': 'language',
    'location': 'location', 'country': 'location', 'city': 'location',
    'email': 'email', 'e-mail': 'email',
    'website': 'website', 'site': 'website', 'web': 'website'
}

def normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names to a standard, lowercase, underscore-separated format."""
    df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
    df.rename(columns=HEADER_MAPPING, inplace=True)
    return df

def clean_text(value, default: str = "") -> str:
    """
    Clean text by stripping whitespace, removing duplicate spaces, and handling nulls/NaNs.
    Converts None, NaN, numpy.nan, empty, or whitespace-only values into `default` (default "").
    Never returns None by default, preventing NOT NULL database constraint violations.
    """
    if value is None or pd.isna(value):
        return default
    
    if isinstance(value, float) and np.isnan(value):
        return default

    text = str(value).strip()
    text = re.sub(r'\s+', ' ', text)  # Collapse multiple whitespace characters into single space
    return text if text else default

def parse_followers(value, default: int = 0) -> int:
    """
    Convert string/numeric representations of followers/following/posts to non-negative integers.
    Handles '12K', '3.5M', '45,000', floats, NaNs, and invalid strings cleanly.
    """
    if value is None or pd.isna(value):
        return default
    
    if isinstance(value, float) and np.isnan(value):
        return default

    clean_val = str(value).replace(',', '').replace(' ', '').upper()
    if clean_val == '' or clean_val.lower() in ('n/a', 'none', 'null', 'nan', 'unknown'):
        return default
    
    match = re.match(r'^([\d\.]+)([KMB]?)$', clean_val)
    if match:
        try:
            num = float(match.group(1))
            suffix = match.group(2)
            
            if suffix == 'K':
                num *= 1_000
            elif suffix == 'M':
                num *= 1_000_000
            elif suffix == 'B':
                num *= 1_000_000_000
                
            return max(0, int(num))
        except (ValueError, OverflowError):
            return default
    
    try:
        val = int(float(clean_val))
        return max(0, val)
    except (ValueError, TypeError, OverflowError):
        return default

def normalize_platform(value, default: str = 'OTHER') -> str:
    """Normalize platform names to match Django model choices."""
    cleaned = clean_text(value, default="")
    if not cleaned:
        return default
    
    val = cleaned.lower()
    if 'insta' in val:
        return 'INSTAGRAM'
    if 'youtube' in val or 'yt' in val:
        return 'YOUTUBE'
    if 'twitter' in val or 'x.com' in val:
        return 'TWITTER'
    if 'facebook' in val or 'fb' in val:
        return 'FACEBOOK'
    if 'linkedin' in val or 'li' in val:
        return 'LINKEDIN'
    
    return default

def clean_json(value, default: dict | None = None) -> dict:
    """Normalize JSON/dict inputs, ensuring a non-null dict is returned."""
    if default is None:
        default = {}
    if value is None or pd.isna(value):
        return default
    if isinstance(value, dict):
        return value
    return default

def clean_list(value, default: list | None = None) -> list:
    """Normalize list inputs, ensuring a non-null list is returned."""
    if default is None:
        default = []
    if value is None or pd.isna(value):
        return default
    if isinstance(value, list):
        return value
    return default

def normalize_influencer_dict(row: dict) -> dict:
    """
    Centralized normalization for Influencer record attributes from any input source
    (CSV, Excel, API responses). Guarantees no NULL values are passed to non-null fields.
    """
    return {
        'name': clean_text(row.get('name')),
        'handle': clean_text(row.get('handle')),
        'platform': normalize_platform(row.get('platform')),
        'followers': parse_followers(row.get('followers')),
        'following': parse_followers(row.get('following')),
        'total_posts': parse_followers(row.get('posts', row.get('total_posts'))),
        'bio': clean_text(row.get('bio')),
        'description': clean_text(row.get('description')),
        'language': clean_text(row.get('language')),
        'location': clean_text(row.get('location')),
        'profile_url': clean_text(row.get('profile_url')),
        'email': clean_text(row.get('email')),
        'website': clean_text(row.get('website')),
        'external_id': clean_text(row.get('external_id')),
    }