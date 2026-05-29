import urllib.request
import urllib.parse
import json
import time
import re
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger("hacker_news_service")

FALLBACK_IMAGE = "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=2070&auto=format&fit=crop"

def _extract_og_image(url: str) -> str:
    """Attempt to quickly fetch the OpenGraph image from the target URL."""
    if "news.ycombinator.com" in url:
        return FALLBACK_IMAGE
        
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'InsightGraph/1.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            html = response.read().decode('utf-8', errors='ignore')
            # Look for <meta property="og:image" content="...">
            match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
            if match:
                return match.group(1)
    except Exception:
        pass
    return FALLBACK_IMAGE

def _fetch_hn_item(item_id: int) -> Dict:
    url = f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json"
    req = urllib.request.Request(url, headers={'User-Agent': 'InsightGraph/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception:
        return {}

def _get_top_comments(kids: List[int], max_comments: int = 5) -> str:
    comments_text = []
    for kid_id in kids[:max_comments]:
        kid_data = _fetch_hn_item(kid_id)
        if kid_data and not kid_data.get('deleted') and not kid_data.get('dead') and 'text' in kid_data:
            from html import unescape
            import re
            # Basic HTML strip
            text = re.sub(r'<[^>]+>', ' ', kid_data['text'])
            text = unescape(text).strip()
            comments_text.append(f"- {text}")
            time.sleep(0.1) # Respect API limits
    return "\n\n".join(comments_text)

def fetch_hacker_news(topics: List[str] = None, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Fetches the latest trending AI stories from Hacker News and pulls their top comments.
    """
    all_results = []
    
    query = "AI"
    if topics and len(topics) > 0:
        query = topics[0]  # Algolia struggles with massive OR queries, use the primary topic
        
    encoded_query = urllib.parse.quote(query)
    # Search algolia for recent high-score stories
    url = f"http://hn.algolia.com/api/v1/search?query={encoded_query}&tags=story&numericFilters=points>50"
    
    try:
        logger.info(f"Fetching Hacker News stories with query: {query}")
        req = urllib.request.Request(url, headers={'User-Agent': 'InsightGraph/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        hits = data.get('hits', [])[:max_results]
        
        for hit in hits:
            story_id = hit.get('objectID')
            title = hit.get('title', '')
            url = hit.get('url', f"https://news.ycombinator.com/item?id={story_id}")
            
            # Fetch the actual item from Firebase to get comment IDs (kids)
            story_data = _fetch_hn_item(story_id)
            kids = story_data.get('kids', [])
            
            comments_block = "No comments available."
            if kids:
                comments_block = _get_top_comments(kids, max_comments=5)
                
            content = f"Article Title: {title}\n\nTop Community Comments:\n{comments_block}"
            
            all_results.append({
                "title": title,
                "url": url,
                "content": content,
                "image_url": _extract_og_image(url),
                "source": "hacker_news",
                "stars": hit.get('points', 0) # Map upvotes to stars field for generic scoring if needed
            })
            
        logger.info(f"Retrieved {len(all_results)} stories from Hacker News.")
        
    except Exception as e:
        logger.error(f"Error fetching from Hacker News: {e}")
        
    return all_results
