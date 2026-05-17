import os
from tavily import TavilyClient
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

def fetch_ai_news(query: str = "latest artificial intelligence advancements and news", max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Fetches the latest AI news using the Tavily API.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is missing.")
    
    client = TavilyClient(api_key=api_key)
    
    try:
        response = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results,
            include_raw_content=False
        )
        
        results = []
        for result in response.get("results", []):
            results.append({
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "source": "tavily"
            })
        return results
    except Exception as e:
        print(f"Error fetching from Tavily: {e}")
        return []
