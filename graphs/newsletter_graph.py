from langgraph.graph import StateGraph, END
from models.state import PipelineState
from agents.retriever import retrieve_articles
from agents.validator import validate_articles
from agents.ranker import rank_articles
from agents.analyzer import analyze_articles
from agents.evaluator import evaluate_newsletter
from agents.composer import compose_newsletter
from utils.logger import get_logger

logger = get_logger("graph")

def route_after_analysis(state: PipelineState) -> str:
    """
    Conditional routing function to decide whether to retry analysis on failure.
    """
    has_issues = len(state.errors) > 0 or len(state.warnings) > 0
    if has_issues:
        logger.info("[Graph] Analyzer finished with some isolated errors. Routing to Evaluator to drop failed articles.")
    else:
        logger.info("[Graph] Analyzer completed successfully. Routing from Analyzer → Evaluator.")
    return "evaluator"

def route_after_evaluation(state: PipelineState) -> str:
    """
    Conditional routing function to evaluate output quality and diversity before composition.
    """
    valid_articles = state.articles
    has_tavily = any(a.source == "tavily" for a in valid_articles)
    avg_trend_score = sum(a.trend_score for a in valid_articles) / len(valid_articles) if valid_articles else 0.0
    
    from config.settings import TARGET_FINAL_ARTICLES
    needs_recovery = (
        len(valid_articles) < TARGET_FINAL_ARTICLES or
        not has_tavily or
        avg_trend_score < 2.0
    )
    
    if needs_recovery:
        if state.retry_count < 0:                                             
            logger.info(f"[Graph] Quality/Diversity check failed. Routing from Evaluator → Retriever (Retry {state.retry_count + 1}/{state.max_retries}).")
            return "retriever"
        else:
            logger.warning("[Graph] Quality/Diversity check failed, but max recovery retries reached. Routing from Evaluator → Composer (Graceful fallback).")
            return "composer"
            
    logger.info("[Graph] Quality/Diversity check passed. Routing from Evaluator → Composer.")
    return "composer"

def create_newsletter_graph():
    """
    Compiles the adaptive, resilient InsightGraph pipeline into a LangGraph StateGraph.
    """
    workflow = StateGraph(PipelineState)

    workflow.add_node("retriever", retrieve_articles)
    workflow.add_node("validator", validate_articles)
    workflow.add_node("ranker", rank_articles)
    workflow.add_node("analyzer", analyze_articles)
    workflow.add_node("evaluator", evaluate_newsletter)
    workflow.add_node("composer", compose_newsletter)

                         
    workflow.set_entry_point("retriever")

                        
    workflow.add_edge("retriever", "validator")
    workflow.add_edge("validator", "ranker")
    workflow.add_edge("ranker", "analyzer")
    
                                        
    workflow.add_conditional_edges(
        "analyzer",
        route_after_analysis,
        {
            "analyzer": "analyzer",
            "evaluator": "evaluator"
        }
    )
    
                                         
    workflow.add_conditional_edges(
        "evaluator",
        route_after_evaluation,
        {
            "retriever": "retriever",
            "composer": "composer"
        }
    )
    
    workflow.add_edge("composer", END)

    return workflow.compile()
