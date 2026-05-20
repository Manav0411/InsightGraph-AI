import time
from models.state import PipelineState
from utils.logger import get_logger
from config.settings import MIN_TREND_SCORE, MIN_SUMMARY_WORDS

logger = get_logger("evaluator")

def evaluate_newsletter(state: PipelineState) -> PipelineState:
    """
    Agent responsible for basic validation of the articles and summaries.
    Filters out any articles that failed generation, are malformed, or have low intelligence signal.
    Operates purely on the PipelineState object.
    """
    start_time = time.perf_counter()
    state.pipeline_stage = "evaluation"
    logger.info("Evaluating generated content...")
    
    if not state.articles:
        logger.warning("Evaluation failed: No articles provided.")
        state.warnings.append("Evaluator received empty article list.")
        return state
        
    seen_titles = set()
    valid_articles = []
    
    for article in state.articles:
        title = article.title
        summary = article.summary or ""
        why_it_matters = article.why_it_matters or ""
        tags = article.tags
        trend_score = article.trend_score
        
        # 1. Reject failed or malformed content
        if not summary or "Summary generation failed." in summary or "Analysis failed." in why_it_matters:
            logger.warning(f"Evaluation Warning: Article '{title}' has an invalid summary or analysis. Removing.")
            state.metadata.total_articles_rejected += 1
            continue
            
        # 2. Reject duplicate titles
        if title in seen_titles:
            logger.warning(f"Evaluation Warning: Duplicate article found '{title}'. Removing.")
            state.metadata.total_articles_rejected += 1
            continue
            
        # 3. Reject missing tags
        if not tags or len(tags) == 0:
            logger.warning(f"Evaluation Warning: Article '{title}' is missing topic tags. Removing.")
            state.metadata.total_articles_rejected += 1
            continue
            
        # 4. Reject low-information or overly generic summaries
        if len(summary.split()) < MIN_SUMMARY_WORDS or "will transform the future" in summary.lower():
            logger.warning(f"Evaluation Warning: Article '{title}' has a vague or low-information summary. Removing.")
            state.metadata.total_articles_rejected += 1
            continue
            
        # 5. Reject low trend score
        if trend_score < MIN_TREND_SCORE:
            logger.warning(f"Evaluation Warning: Article '{title}' has a low trend score ({trend_score}). Removing.")
            state.metadata.total_articles_rejected += 1
            continue
            
        seen_titles.add(title)
        valid_articles.append(article)
        
    state.articles = valid_articles
    
    elapsed_time = round(time.perf_counter() - start_time, 2)
    state.metadata.agent_timings["evaluator"] = elapsed_time
    
    logger.info(f"[Evaluator] Rejected {state.metadata.total_articles_rejected} low-quality articles.")
    logger.info(f"[Evaluator] Evaluation completed. Retained {len(valid_articles)} valid articles.")
    logger.info(f"[Evaluator] Completed in {elapsed_time}s")
    
    return state
