import time
import re
from models.state import PipelineState
from utils.logger import get_logger

logger = get_logger("validator")

def validate_articles(state: PipelineState) -> PipelineState:
    """
    Validates retrieved articles to ensure title-content relevance before downstream processing.
    Filters out noisy or unrelated articles using deterministic heuristics.
    """
    start_time = time.perf_counter()
    state.pipeline_stage = "validation"
    logger.info("Validating retrieved articles for grounding...")
    
    valid_articles = []
    
    # Simple stop words to ignore in keyword extraction
    stop_words = {"a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "or", "with", "is", "are", "was", "were", "it", "this", "that", "by", "as", "from", "be", "how", "what", "why", "new", "about"}
    
    for article in state.articles:
        title = article.title.lower()
        content = article.content.lower()
        
        # Extract keywords from title (alphanumeric only)
        title_words = re.findall(r'\b\w+\b', title)
        keywords = {word for word in title_words if word not in stop_words and len(word) > 2}
        
        if not keywords:
            # If no meaningful keywords, let it pass (edge case)
            valid_articles.append(article)
            continue
            
        # Count how many title keywords appear in the content
        match_count = sum(1 for kw in keywords if kw in content)
        overlap_ratio = match_count / len(keywords)
        
        # Require at least some overlap to consider the content grounded to the title
        # For small titles (1-3 keywords), require at least 1 match. 
        # For larger titles, require at least 20% overlap.
        if overlap_ratio >= 0.2 or match_count >= 1:
            valid_articles.append(article)
        else:
            logger.warning(f"[Validator] Rejected article due to low title-content relevance: '{article.title}'")
            state.metadata.total_articles_rejected += 1
            state.metadata.validation_failures += 1
            
    total_articles = len(state.articles)
    state.articles = valid_articles
    
    elapsed_time = round(time.perf_counter() - start_time, 2)
    state.metadata.agent_timings["validator"] = elapsed_time
    
    logger.info(f"[Validator] Validated {len(valid_articles)}/{total_articles} articles.")
    logger.info(f"[Validator] Completed in {elapsed_time}s")
    
    return state
