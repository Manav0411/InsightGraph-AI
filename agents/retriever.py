import time
from typing import Dict, Any, List
from services.tavily_service import fetch_ai_news
from services.github_service import fetch_github_trends
from models.state import PipelineState, Article
from utils.logger import get_logger

logger = get_logger("retriever")

def retrieve_articles(state: PipelineState) -> PipelineState:
    """
    Agent responsible for retrieving articles from various services.
    Acts as the strict normalization boundary. Converts external raw dicts into Pydantic state.
    """
    start_time = time.perf_counter()
    
    # Detect recovery route transition from Evaluator
    if state.pipeline_stage == "evaluation":
        state.retry_count += 1
        state.metadata.recovery_attempts += 1
        state.metadata.conditional_routes_triggered += 1
        logger.warning(
            f"[Graph] Routing from Evaluator → Retriever. "
            f"Retry Count: {state.retry_count}/{state.max_retries}"
        )
        
    state.pipeline_stage = "retrieval"
    
    recovery_attempts = state.metadata.recovery_attempts
    if recovery_attempts > 0:
        logger.info(f"Starting article retrieval recovery run (attempt {recovery_attempts})...")
    else:
        logger.info("Starting article retrieval...")
        
    # Scale max results dynamically to fetch deeper when retrying
    tavily_max = 5 + recovery_attempts * 3
    github_max = 10 + recovery_attempts * 5
    
    all_articles_raw = []
    
    # Use the user's preferred topics if defined
    user_topics = state.user_profile.preferences.preferred_topics if state.user_profile.preferences.preferred_topics else None

    # 1. Fetch from Tavily Service
    try:
        tavily_articles = fetch_ai_news(queries=user_topics, max_results=tavily_max)
        all_articles_raw.extend(tavily_articles)
        if tavily_articles and "tavily" not in state.metadata.retrieval_sources:
            state.metadata.retrieval_sources.append("tavily")
    except Exception as e:
        logger.error(f"Error retrieving from Tavily service: {e}")
        state.errors.append(f"Tavily retrieval failed: {e}")
        
    # 2. GitHub Integration
    try:
        github_articles = fetch_github_trends(max_results=github_max, topics=user_topics)
        all_articles_raw.extend(github_articles)
        if github_articles and "github" not in state.metadata.retrieval_sources:
            state.metadata.retrieval_sources.append("github")
    except Exception as e:
        logger.error(f"Error retrieving from GitHub service: {e}")
        state.errors.append(f"GitHub retrieval failed: {e}")
        
    # Deduplicate raw fetched articles against themselves based on title.lower()
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
            
    # Deduplicate and append to state.articles (avoiding overwriting previously accepted articles)
    existing_titles = {a.title.strip().lower() for a in state.articles}
    new_articles_count = 0
    
    for raw in deduplicated_raw:
        title = raw.get("title", "Untitled")
        title_lower = title.strip().lower()
        
        if title_lower not in existing_titles:
            article = Article(
                title=title,
                url=raw.get("url", ""),
                content=raw.get("content", ""),
                source=raw.get("source", "unknown"),
                stars=raw.get("stars", None)
            )
            state.articles.append(article)
            existing_titles.add(title_lower)
            new_articles_count += 1
            
    state.metadata.total_articles_retrieved = len(state.articles)
    
    elapsed_time = round(time.perf_counter() - start_time, 2)
    state.metadata.agent_timings["retriever"] = elapsed_time
    
    logger.info(f"[Retriever] Retrieved {len(all_articles_raw)} total raw articles. Appended {new_articles_count} new unique Pydantic Articles.")
    logger.info(f"[Retriever] Completed in {elapsed_time}s")
    
    return state
