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


def route_after_evaluation(state: PipelineState) -> str:
    """
    After evaluation, decide whether the result is thin enough to warrant one
    recovery pass back through the retriever (which scales up its search limits),
    or whether to proceed to composition.
    """
    from config.settings import TARGET_FINAL_ARTICLES

    valid_articles = state.articles
    has_tavily = any(a.source == "tavily" for a in valid_articles)
    avg_trend_score = (
        sum(a.trend_score for a in valid_articles) / len(valid_articles)
        if valid_articles else 0.0
    )

    needs_recovery = (
        len(valid_articles) < TARGET_FINAL_ARTICLES
        or not has_tavily
        or avg_trend_score < 2.0
    )

    if needs_recovery and state.retry_count < state.max_retries:
        logger.info(
            f"[Graph] Quality/diversity check failed. Evaluator → Retriever "
            f"(recovery {state.retry_count + 1}/{state.max_retries})."
        )
        return "retriever"

    if needs_recovery:
        logger.warning(
            "[Graph] Quality/diversity check failed but recovery budget exhausted. "
            "Evaluator → Composer (degraded)."
        )
    else:
        logger.info("[Graph] Quality/diversity check passed. Evaluator → Composer.")
    return "composer"


def create_newsletter_graph():
    """
    Compiles the adaptive InsightGraph pipeline into a LangGraph StateGraph.

    retriever → validator → ranker → analyzer → evaluator → (composer | retriever)
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
    workflow.add_edge("analyzer", "evaluator")

    workflow.add_conditional_edges(
        "evaluator",
        route_after_evaluation,
        {
            "retriever": "retriever",
            "composer": "composer",
        },
    )

    workflow.add_edge("composer", END)

    return workflow.compile()
