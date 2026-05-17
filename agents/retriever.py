from typing import Dict, Any, List
from services.tavily_service import fetch_ai_news

def retrieve_articles() -> Dict[str, List[Dict[str, Any]]]:
    """
    Agent responsible for retrieving articles from various services.
    Currently only uses Tavily.
    """
    print("Retrieving articles via Tavily...")
    articles = fetch_ai_news(query="latest breakthroughs in artificial intelligence today", max_results=5)
    return {
        "articles": articles
    }
