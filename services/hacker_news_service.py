import urllib.request
import urllib.parse
import json
import time
import re
import os
from typing import List, Dict, Any
from utils.logger import get_logger
from utils.image_utils import extract_og_image

logger = get_logger("hacker_news_service")

CACHE_FILE = "/tmp/insightgraph_hn_cache.json"

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
    Fetches a broad batch of 30 stories and filters them locally by topic.
    """
    all_results = []
    
    # Always fetch a broad list of top AI stories (limit 30)
    query = "AI"
    encoded_query = urllib.parse.quote(query)
    url = f"http://hn.algolia.com/api/v1/search?query={encoded_query}&tags=story&numericFilters=points>50&hitsPerPage=30"
    
    try:
        logger.info(f"Fetching broad batch of 30 Hacker News AI stories for local filtering...")
        req = urllib.request.Request(url, headers={'User-Agent': 'InsightGraph/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        raw_hits = data.get('hits', [])
        filtered_hits = []
        
        # Local Filtering: Match against preferred topics
        if topics and len(topics) > 0:
            lowercase_topics = [t.lower() for t in topics]
            for hit in raw_hits:
                text_to_search = (hit.get('title', '') + " " + hit.get('story_text', '')).lower()
                # If any topic keyword is in the text, keep it
                if any(topic in text_to_search for topic in lowercase_topics):
                    filtered_hits.append(hit)
        else:
            filtered_hits = raw_hits
            
        # Take the top max_results after filtering
        final_hits = filtered_hits[:max_results]
        
        if not final_hits and raw_hits:
            logger.warning("Local HN filter removed all 30 stories! Falling back to top 3 generic AI stories.")
            final_hits = raw_hits[:3]
        
        for hit in final_hits:
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
                "image_url": extract_og_image(url),
                "source": "hacker_news",
                "stars": hit.get('points', 0) # Map upvotes to stars field for generic scoring if needed
            })
            
        logger.info(f"Retrieved {len(all_results)} filtered stories from Hacker News.")
        
        # Cache the successful results to disk
        if all_results:
            try:
                with open(CACHE_FILE, 'w') as f:
                    json.dump(all_results, f)
            except Exception as e:
                logger.warning(f"Failed to write HN cache: {e}")
                
    except Exception as e:
        logger.error(f"Error fetching from Hacker News: {e}. Attempting to load from cache...")
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r') as f:
                    all_results = json.load(f)
                    logger.info(f"Loaded {len(all_results)} Hacker News stories from local cache.")
            except Exception as cache_e:
                logger.error(f"Failed to load HN cache: {cache_e}")
        
    return all_results
