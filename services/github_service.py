import requests
import datetime
from typing import List, Dict, Any

def fetch_github_trends(max_results: int = 10, topics: List[str] = None) -> List[Dict[str, Any]]:
    """
    Fetches trending open-source AI repositories from GitHub.
    Uses the GitHub Search API to find repositories created recently
    with AI-related topics, sorted by stars.
    """
    print("Fetching GitHub trending repositories...")
    
    # Calculate the date for 14 days ago to get recent trends
    recent_date = (datetime.datetime.now() - datetime.timedelta(days=14)).strftime('%Y-%m-%d')
    
    # Query for AI related topics created recently, sorted by stars
    if topics:
        topic_query = " OR ".join(f'"{t}"' for t in topics)
        query = f"{topic_query} created:>{recent_date}"
    else:
        query = f"AI OR LLM OR Agent OR Generative created:>{recent_date}"
        
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc"
    
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AI-Trend-Intelligence-App"
    }
    
    results = []
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        items = data.get("items", [])[:max_results]
        
        for item in items:
            results.append({
                "title": item.get("name", ""),
                "url": item.get("html_url", ""),
                "image_url": f"https://opengraph.githubassets.com/1/{item.get('full_name')}" if item.get("full_name") else None,
                "content": item.get("description", "") or "No description provided.",
                "source": "github",
                "stars": item.get("stargazers_count", 0)
            })
            
        print(f"Retrieved {len(results)} GitHub repositories")
    except Exception as e:
        print(f"Error fetching GitHub trends: {e}")
        
    return results
