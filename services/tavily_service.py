import os
from tavily import TavilyClient
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Pre-defined focused queries targeting concrete AI updates rather than broad prediction blogs
DEFAULT_QUERIES = [
    "latest AI agent developments",
    "latest LLM releases",
    "AI coding assistants news",
    "open source AI model releases",
    "LangGraph AI agents",
    "AI startup funding",
    "latest AI research breakthroughs"
]

def fetch_ai_news(queries: List[str] = None, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Fetches the latest AI news using the Tavily API.
    Iterates over multiple queries, retrieving top 3-5 articles for each,
    with a focus on news from the past week (days=7).
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY environment variable is missing.")
    
    client = TavilyClient(api_key=api_key)
    
    if queries is None:
        queries = DEFAULT_QUERIES
        
    all_results = []
    
    for query in queries:
        print(f"Fetching query: {query}")
        try:
            response = client.search(
                query=query,
                search_depth="advanced",
                topic="news",
                days=7,
                max_results=max_results,
                include_raw_content=False
            )
            
            results = response.get("results", [])
            print(f"Retrieved {len(results)} articles")
            
            for result in results:
                all_results.append({
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": result.get("content", ""),
                    "source": "tavily"
                })
        except Exception as e:
            print(f"Error fetching query '{query}' from Tavily: {e}")
            
    return all_results
