import time
from models.state import PipelineState
from utils.logger import get_logger
from config.settings import MIN_TREND_SCORE, MIN_SUMMARY_WORDS, TARGET_FINAL_ARTICLES

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
        
                                               
        if not summary or "Summary generation failed." in summary or "Analysis failed." in why_it_matters:
            logger.warning(f"Evaluation Warning: Article '{title}' has an invalid summary or analysis. Removing.")
            state.metadata.total_articles_rejected += 1
            continue
            
                                    
        if title in seen_titles:
            logger.warning(f"Evaluation Warning: Duplicate article found '{title}'. Removing.")
            state.metadata.total_articles_rejected += 1
            continue
            
                                
        if not tags or len(tags) == 0:
            logger.warning(f"Evaluation Warning: Article '{title}' is missing topic tags. Removing.")
            state.metadata.total_articles_rejected += 1
            continue
            
                                                               
        if len(summary.split()) < MIN_SUMMARY_WORDS or "will transform the future" in summary.lower():
            logger.warning(f"Evaluation Warning: Article '{title}' has a vague or low-information summary. Removing.")
            state.metadata.total_articles_rejected += 1
            continue
            
        if len(why_it_matters.strip()) < 30:
            logger.warning(f"Evaluation Warning: Article '{title}' has a too short why_it_matters analysis. Removing.")
            state.metadata.total_articles_rejected += 1
            continue
            
        if not article.details or len(article.details) < 2:
            logger.warning(f"Evaluation Warning: Article '{title}' lacks sufficient concrete details (less than 2 bullets). Removing.")
            state.metadata.total_articles_rejected += 1
            continue
            
                                   
        if trend_score < MIN_TREND_SCORE:
            logger.warning(f"Evaluation Warning: Article '{title}' has a low trend score ({trend_score}). Removing.")
            state.metadata.total_articles_rejected += 1
            continue
            
                                                     
        import re
        title_words_for_eval = re.findall(r'\b\w+\b', title.lower())
        stop_words = {"a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "or", "with", "is", "are", "was", "were", "it", "this", "that", "by", "as", "from", "be", "how", "what", "why", "new", "about"}
        keywords = {word for word in title_words_for_eval if word not in stop_words and len(word) > 2}
        
        summary_lower = summary.lower()
        if keywords:
            match_count = sum(1 for kw in keywords if kw in summary_lower)
            overlap_ratio = match_count / len(keywords)
            
                                                                                                                 
            if overlap_ratio < 0.1 and match_count == 0:
                logger.warning(f"[Evaluator] Rejected hallucinated/misaligned summary for article: '{title}'")
                state.metadata.total_articles_rejected += 1
                state.metadata.grounding_rejections += 1
                continue
            
        seen_titles.add(title)
        valid_articles.append(article)
        
    state.articles = valid_articles
    
                                                                  
    has_tavily = any(a.source == "tavily" for a in valid_articles)
    avg_trend_score = sum(a.trend_score for a in valid_articles) / len(valid_articles) if valid_articles else 0.0
    
    if len(valid_articles) < 5:
        logger.warning(f"[Evaluator] Warning: Insufficient valid articles count ({len(valid_articles)}/5).")
    if not has_tavily:
        logger.warning("[Evaluator] Warning: Source diversity check failed. No Tavily news articles found.")
    if avg_trend_score < 2.0:
        logger.warning(f"[Evaluator] Warning: Average trend score is below baseline ({round(avg_trend_score, 2)} < 2.0).")
        
                                                                              
    if len(valid_articles) > TARGET_FINAL_ARTICLES:
        from collections import defaultdict
        
        source_groups = defaultdict(list)
        for a in valid_articles:
            source_groups[a.source].append(a)
            
        final_list = []
        num_sources = len(source_groups)
        
        if num_sources > 0:
            target_per_source = TARGET_FINAL_ARTICLES // num_sources
            
                                                             
            for source, articles in source_groups.items():
                                                                                   
                taken = articles[:target_per_source]
                final_list.extend(taken)
                
                                                      
                source_groups[source] = articles[len(taken):]
                
                                                                                      
            remaining_slots = TARGET_FINAL_ARTICLES - len(final_list)
            if remaining_slots > 0:
                unused = []
                for articles in source_groups.values():
                    unused.extend(articles)
                
                unused.sort(key=lambda x: x.trend_score, reverse=True)
                final_list.extend(unused[:remaining_slots])
                
                                               
        final_list.sort(key=lambda x: x.trend_score, reverse=True)
        valid_articles = final_list
    
    state.articles = valid_articles
    elapsed_time = round(time.perf_counter() - start_time, 2)
    state.metadata.agent_timings["evaluator"] = elapsed_time
    
    logger.info(f"[Evaluator] Rejected {state.metadata.total_articles_rejected} low-quality articles.")
    logger.info(f"[Evaluator] Evaluation completed. Retained {len(valid_articles)} valid articles for the final newsletter.")
    logger.info(f"[Evaluator] Completed in {elapsed_time}s")
    
    return state
