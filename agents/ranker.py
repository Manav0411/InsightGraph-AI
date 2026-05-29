import time
from models.state import PipelineState
from utils.logger import get_logger
from config.settings import MAX_ARTICLES_TO_ANALYZE

logger = get_logger("ranker")

def rank_articles(state: PipelineState) -> PipelineState:
    """
    Agent responsible for computing a heuristic trend_score for each article 
    and returning only the highest-signal items to be analyzed.
    Operates purely on the PipelineState object.
    """
    start_time = time.perf_counter()
    state.pipeline_stage = "ranking"
    logger.info("Ranking and scoring retrieved articles...")
    
    user_profile = state.user_profile
    boosts_applied_total = 0
    if user_profile:
        state.metadata.generated_for_user = user_profile.user_id
        logger.info(f"Applying personalization boosts for user: {user_profile.user_id}")
    
    for article in state.articles:
        score = 0.0
        source = article.source
        title = article.title.lower()
        content = article.content.lower()
        
        # Generic metric heuristic: reward highly upvoted/starred posts (Logarithmic scale)
        # Applies to Hacker News, Reddit, or any source setting 'stars'
        metrics = article.stars or 0
        if metrics > 0:
            import math
            score += math.log10(metrics)  # e.g., 1000 upvotes -> +3.0
            
        # Content keywords heuristics (generic quality markers)
        if "breakthrough" in content or "state-of-the-art" in content or "sota" in content:
            score += 2.0
            
        # Default baseline
        score += 1.0
        
        # Personalization boost logic
        p_boost = 0.0
        if user_profile:
            prefs = user_profile.preferences
            # Preferred sources match (case-insensitive)
            for pref_source in prefs.preferred_sources:
                if pref_source.lower() == source.lower():
                    p_boost += 2.0
                    boosts_applied_total += 1
                    article.recommendation_reasons.append(f"Preferred source: {pref_source} (+2.0)")
                    logger.info(f"Article '{article.title}' matched preferred source '{pref_source}': +2.0 boost")
            
            # Preferred topics match (case-insensitive)
            for pref_topic in prefs.preferred_topics:
                pref_topic_lower = pref_topic.lower()
                if pref_topic_lower in title or pref_topic_lower in content:
                    p_boost += 3.0
                    boosts_applied_total += 1
                    article.recommendation_reasons.append(f"Matches preferred topic: {pref_topic} (+3.0)")
                    logger.info(f"Article '{article.title}' matched preferred topic '{pref_topic}': +3.0 boost")
            
            # Excluded topics match (case-insensitive)
            for excl_topic in prefs.excluded_topics:
                excl_topic_lower = excl_topic.lower()
                if excl_topic_lower in title or excl_topic_lower in content:
                    p_boost -= 5.0
                    boosts_applied_total += 1
                    article.recommendation_reasons.append(f"Matches excluded topic: {excl_topic} (-5.0)")
                    logger.info(f"Article '{article.title}' matched excluded topic '{excl_topic}': -5.0 penalty")

        article.personalization_boost = round(p_boost, 1)
        score += p_boost
        
        # Cap score rounding
        article.trend_score = round(score, 1)
        
    if user_profile:
        state.metadata.personalization_boosts_applied = boosts_applied_total
        logger.info(f"Total personalization boosts/penalties applied: {boosts_applied_total}")
        
    # Sort articles by trend_score descending
    state.articles = sorted(state.articles, key=lambda x: x.trend_score, reverse=True)
    
    # Keep top articles based on config for downstream analysis buffer
    top_articles = state.articles[:MAX_ARTICLES_TO_ANALYZE]
    
    elapsed_time = round(time.perf_counter() - start_time, 2)
    state.metadata.agent_timings["ranker"] = elapsed_time
    
    logger.info(f"[Ranker] Ranked {len(state.articles)} articles. Kept top {len(top_articles)} for downstream analysis.")
    logger.info(f"[Ranker] Completed in {elapsed_time}s")
    
    state.articles = top_articles
    return state
