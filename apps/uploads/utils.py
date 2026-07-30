import re
import pandas as pd

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

def clean_text(value) -> str | None:
    """Clean text by stripping whitespace, removing duplicate spaces, and handling nulls."""
    if pd.isna(value) or value is None:
        return None
    text = str(value).strip()
    text = re.sub(r'\s+', ' ', text)  # Remove duplicate spaces
    return text if text else None

def parse_followers(value) -> int:
    """Convert string representations of followers (e.g., '12K', '3.5M', '45,000') to integers."""
    if pd.isna(value) or value == '':
        return 0
    
    # Remove commas and spaces, convert to uppercase for consistent matching
    clean_val = str(value).replace(',', '').replace(' ', '').upper()
    
    # Match numbers (including decimals) followed by an optional K, M, or B suffix
    match = re.match(r'^([\d\.]+)([KMB]?)$', clean_val)
    if match:
        num = float(match.group(1))
        suffix = match.group(2)
        
        if suffix == 'K':
            num *= 1_000
        elif suffix == 'M':
            num *= 1_000_000
        elif suffix == 'B':
            num *= 1_000_000_000
            
        return int(num)
    
    # Fallback: try to parse as direct integer
    try:
        return int(float(clean_val))
    except ValueError:
        return 0

def normalize_platform(value) -> str:
    """Normalize platform names to match Django model choices."""
    if not value:
        return 'OTHER'
    
    val = str(value).strip().lower()
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
    
    return 'OTHER'