import urllib.request
import re
from utils.logger import get_logger

logger = get_logger("image_utils")

FALLBACK_IMAGE = "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=2070&auto=format&fit=crop"

def extract_og_image(url: str, default_image: str = FALLBACK_IMAGE) -> str:
    """
    Attempt to quickly fetch the OpenGraph image from the target URL.
    Returns the default_image if extraction fails.
    """
    if "news.ycombinator.com" in url:
        return default_image
        
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'InsightGraph/1.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            html = response.read().decode('utf-8', errors='ignore')
            # Look for <meta property="og:image" content="...">
            match = re.search(r'<meta property="og:image"\s+content="([^"]+)"', html, re.IGNORECASE)
            if not match:
                # Also try <meta name="og:image" content="...">
                match = re.search(r'<meta name="og:image"\s+content="([^"]+)"', html, re.IGNORECASE)
                
            if match:
                return match.group(1)
    except Exception:
        pass
        
    return default_image
