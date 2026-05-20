from typing import Dict, Any, List
from services.tavily_service import fetch_ai_news
from services.github_service import fetch_github_trends
from models.state import PipelineState, Article
from utils.logger import get_logger

logger = get_logger("retriever")

def retrieve_articles() -> PipelineState:
    """
    Agent responsible for retrieving articles from various services.
    Acts as the strict normalization boundary. Converts external raw dicts into Pydantic state.
    """
    state = PipelineState()
    state.pipeline_stage = "retrieval"
    
    logger.info("Starting article retrieval...")
    all_articles_raw = []
    
    # 1. Fetch from Tavily Service
    try:
        tavily_articles = fetch_ai_news()
        all_articles_raw.extend(tavily_articles)
        if tavily_articles:
            state.metadata.retrieval_sources.append("tavily")
    except Exception as e:
        logger.error(f"Error retrieving from Tavily service: {e}")
        state.errors.append(f"Tavily retrieval failed: {e}")
        
    # 2. GitHub Integration
    try:
        github_articles = fetch_github_trends()
        all_articles_raw.extend(github_articles)
        if github_articles:
            state.metadata.retrieval_sources.append("github")
    except Exception as e:
        logger.error(f"Error retrieving from GitHub service: {e}")
        state.errors.append(f"GitHub retrieval failed: {e}")
        
    # Deduplicate articles based on title.lower()
    deduplicated_raw = []
    seen_titles = set()
    
    for raw in all_articles_raw:
        title = raw.get("title", "")
        title_lower = title.strip().lower()
        
        # Skip articles with empty titles
        if not title_lower:
            continue
            
        if title_lower not in seen_titles:
            seen_titles.add(title_lower)
            deduplicated_raw.append(raw)
            
    # Normalize to Pydantic Articles
    for raw in deduplicated_raw:
        article = Article(
            title=raw.get("title", "Untitled"),
            url=raw.get("url", ""),
            content=raw.get("content", ""),
            source=raw.get("source", "unknown"),
            stars=raw.get("stars", None)
        )
        state.articles.append(article)
            
    state.metadata.total_articles_retrieved = len(state.articles)
    
    logger.info(f"Retrieved {len(all_articles_raw)} total articles. Deduplicated to {len(state.articles)} unique Pydantic Articles.")
    
    return state
