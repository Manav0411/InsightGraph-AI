from typing import Dict, Any, List
from services.tavily_service import fetch_ai_news

# Ready for future service integrations:
# from services.github_service import fetch_github_trends
# from services.arxiv_service import fetch_arxiv_papers
# from services.reddit_service import fetch_reddit_posts

def retrieve_articles() -> Dict[str, List[Dict[str, Any]]]:
    """
    Agent responsible for retrieving articles from various services.
    Combines all sources, standardizes outputs, and deduplicates using title.lower().
    """
    print("Starting article retrieval...")
    all_articles = []
    
    # 1. Fetch from Tavily Service
    # Returns standardized format: {"title": "...", "url": "...", "content": "...", "source": "tavily"}
    try:
        tavily_articles = fetch_ai_news()
        all_articles.extend(tavily_articles)
    except Exception as e:
        print(f"Error retrieving from Tavily service: {e}")
        
    # 2. GitHub Integration (Future extension)
    # try:
    #     github_articles = fetch_github_trends()
    #     all_articles.extend(github_articles)
    # except Exception as e:
    #     print(f"Error retrieving from GitHub service: {e}")
        
    # 3. arXiv Integration (Future extension)
    # try:
    #     arxiv_articles = fetch_arxiv_papers()
    #     all_articles.extend(arxiv_articles)
    # except Exception as e:
    #     print(f"Error retrieving from arXiv service: {e}")
        
    # 4. Reddit Integration (Future extension)
    # try:
    #     reddit_articles = fetch_reddit_posts()
    #     all_articles.extend(reddit_articles)
    # except Exception as e:
    #     print(f"Error retrieving from Reddit service: {e}")

    # Deduplicate articles based on title.lower()
    deduplicated_articles = []
    seen_titles = set()
    
    for article in all_articles:
        title = article.get("title", "")
        title_lower = title.strip().lower()
        
        # Skip articles with empty titles
        if not title_lower:
            continue
            
        if title_lower not in seen_titles:
            seen_titles.add(title_lower)
            deduplicated_articles.append(article)
            
    print(f"Retrieved {len(all_articles)} total articles. Deduplicated to {len(deduplicated_articles)} unique articles.")
    
    # Limit processed articles after deduplication to optimize downstream performance and avoid rate limits
    articles = deduplicated_articles[:10]
    
    return {
        "articles": articles
    }
