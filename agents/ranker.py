import re
import time
from models.state import PipelineState
from utils.logger import get_logger
from config.settings import MAX_ARTICLES_TO_ANALYZE

logger = get_logger("ranker")

_STOPWORDS = {"the", "and", "for", "with", "your", "you"}


def _topic_hits(topic: str, text: str) -> bool:
    """
    Whole-word match of an excluded/preferred topic against `text`.

    Matches the full normalized phrase, or any single significant token
    (>= 5 chars). Word boundaries prevent 'sports' matching 'transports'
    and callers pass only the title + lede so an incidental body mention
    (e.g. a GPU article referencing 'gaming') does not trigger a drop.
    """
    text = text.lower()
    normalized = re.sub(r"[^a-z0-9]+", " ", topic.lower()).strip()
    if not normalized:
        return False

    if re.search(rf"\b{re.escape(normalized)}\b", text):
        return True

    tokens = [t for t in normalized.split() if len(t) >= 5 and t not in _STOPWORDS]
    return any(re.search(rf"\b{re.escape(t)}\b", text) for t in tokens)

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
    
    filtered_articles = []
    
    for article in state.articles:
        score = 0.0
        source = article.source
        title = article.title.lower()
        content = article.content.lower()

        # Match topics against the title + lede only. The full body often carries
        # incidental mentions (HN comments, "gaming GPUs" in a chip story) that
        # previously triggered false-positive hard drops on substring matches.
        topic_haystack = f"{article.title}\n{article.content[:300]}"

        should_drop = False
        if user_profile:
            prefs = user_profile.preferences
            for excl_topic in prefs.excluded_topics:
                if _topic_hits(excl_topic, topic_haystack):
                    logger.info(f"Article '{article.title}' matched excluded topic '{excl_topic}'. Hard dropping.")
                    should_drop = True
                    break
        if should_drop:
            continue
            
                                                                                           
                                                                       
        metrics = article.stars or 0
        if metrics > 0:
            import math
            score += math.log10(metrics)                              
            
                                                               
        if "breakthrough" in content or "state-of-the-art" in content or "sota" in content:
            score += 2.0
            
                          
        score += 1.0
        
                                     
        p_boost = 0.0
        if user_profile:
            prefs = user_profile.preferences
                                                        
            for pref_source in prefs.preferred_sources:
                if pref_source.lower() == source.lower():
                    p_boost += 2.0
                    boosts_applied_total += 1
                    article.recommendation_reasons.append(f"Preferred source: {pref_source} (+2.0)")
                    logger.info(f"Article '{article.title}' matched preferred source '{pref_source}': +2.0 boost")
            
            for pref_topic in prefs.preferred_topics:
                if _topic_hits(pref_topic, topic_haystack):
                    p_boost += 3.0
                    boosts_applied_total += 1
                    article.recommendation_reasons.append(f"Matches preferred topic: {pref_topic} (+3.0)")
                    logger.info(f"Article '{article.title}' matched preferred topic '{pref_topic}': +3.0 boost")

        article.personalization_boost = round(p_boost, 1)
        score += p_boost
        
                            
        article.trend_score = round(score, 1)
        filtered_articles.append(article)
        
                                              
    state.articles = filtered_articles
        
    if user_profile:
        state.metadata.personalization_boosts_applied = boosts_applied_total
        logger.info(f"Total personalization boosts/penalties applied: {boosts_applied_total}")
        
                                             
    state.articles = sorted(state.articles, key=lambda x: x.trend_score, reverse=True)
    
                                                                      
    top_articles = state.articles[:MAX_ARTICLES_TO_ANALYZE]
    
    elapsed_time = round(time.perf_counter() - start_time, 2)
    state.metadata.agent_timings["ranker"] = elapsed_time
    
    logger.info(f"[Ranker] Ranked {len(state.articles)} articles. Kept top {len(top_articles)} for downstream analysis.")
    logger.info(f"[Ranker] Completed in {elapsed_time}s")
    
    state.articles = top_articles
    return state
