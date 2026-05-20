from models.state import PipelineState
from utils.logger import get_logger
from config.settings import MAX_ARTICLES

logger = get_logger("ranker")

def rank_articles(state: PipelineState) -> PipelineState:
    """
    Agent responsible for computing a heuristic trend_score for each article 
    and returning only the highest-signal items to be analyzed.
    Operates purely on the PipelineState object.
    """
    state.pipeline_stage = "ranking"
    logger.info("Ranking and scoring retrieved articles...")
    
    for article in state.articles:
        score = 0.0
        source = article.source
        title = article.title.lower()
        content = article.content.lower()
        
        # GitHub specific heuristic: reward highly starred repos
        if source == "github":
            stars = article.stars or 0
            score += stars / 1000.0
            
        # Title keywords heuristics
        if "agent" in title:
            score += 5.0
        if "llm" in title:
            score += 3.0
        if "generative" in title:
            score += 2.0
            
        # Content keywords heuristics
        if "open source" in content or "open-source" in content:
            score += 2.0
        if "breakthrough" in content or "state-of-the-art" in content or "sota" in content:
            score += 2.0
            
        # Default baseline
        score += 1.0
        
        # Cap score rounding
        article.trend_score = round(score, 1)
        
    # Sort articles by trend_score descending
    state.articles = sorted(state.articles, key=lambda x: x.trend_score, reverse=True)
    
    # Keep top articles based on config
    top_articles = state.articles[:MAX_ARTICLES]
    
    logger.info(f"Ranked {len(state.articles)} articles. Kept top {len(top_articles)} for downstream analysis.")
    
    state.articles = top_articles
    return state
