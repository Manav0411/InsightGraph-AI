import urllib.request
import json
import time
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger("reddit_service")

SUBREDDITS = ["MachineLearning", "LocalLLaMA"]
HEADERS = {
    'User-Agent': 'InsightGraphBot/1.0 (by /u/insight_bot)'
}

def _fetch_reddit_comments(permalink: str, max_comments: int = 5) -> str:
    url = f"https://www.reddit.com{permalink}.json"
    req = urllib.request.Request(url, headers=HEADERS)
    comments_text = []
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            if len(data) > 1:
                comments_list = data[1].get('data', {}).get('children', [])
                for child in comments_list[:max_comments]:
                    kind = child.get('kind')
                    if kind == 't1':  # t1 is a comment
                        body = child.get('data', {}).get('body', '').strip()
                        if body and body != '[deleted]':
                            comments_text.append(f"- {body}")
    except Exception:
        pass
        
    return "\n\n".join(comments_text)

def fetch_reddit_trends(max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Fetches the top weekly posts from key AI subreddits and grabs the top comments.
    """
    all_results = []
    
    # We evenly split the max_results across the subreddits
    per_sub = max(1, max_results // len(SUBREDDITS))
    
    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/top.json?t=week&limit={per_sub}"
        try:
            logger.info(f"Fetching top weekly posts from r/{sub}")
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                
            children = data.get('data', {}).get('children', [])
            
            for child in children:
                post_data = child.get('data', {})
                title = post_data.get('title', '')
                permalink = post_data.get('permalink', '')
                url = f"https://www.reddit.com{permalink}"
                selftext = post_data.get('selftext', '')
                
                # Fetch comments
                comments_block = _fetch_reddit_comments(permalink)
                
                content = f"Post Title: {title}\n"
                if selftext:
                    content += f"\nPost Body:\n{selftext[:1000]}\n"
                if comments_block:
                    content += f"\nTop Community Comments:\n{comments_block}"
                    
                if len(content.strip()) < 50:
                    continue
                    
                all_results.append({
                    "title": title,
                    "url": url,
                    "content": content,
                    "image_url": None,
                    "source": "reddit",
                    "stars": post_data.get('score', 0)
                })
                time.sleep(0.5) # Anti-rate limit
                
        except Exception as e:
            logger.error(f"Error fetching from r/{sub}: {e}")
            
    logger.info(f"Retrieved {len(all_results)} posts from Reddit.")
    return all_results
