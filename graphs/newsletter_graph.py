from langgraph.graph import StateGraph, END
from models.state import PipelineState
from agents.retriever import retrieve_articles
from agents.ranker import rank_articles
from agents.analyzer import analyze_articles
from agents.evaluator import evaluate_newsletter
from agents.composer import compose_newsletter

def create_newsletter_graph():
    """
    Compiles the deterministic AI Trend Intelligence pipeline into a LangGraph StateGraph.
    """
    workflow = StateGraph(PipelineState)

    # Add all agent nodes
    workflow.add_node("retriever", retrieve_articles)
    workflow.add_node("ranker", rank_articles)
    workflow.add_node("analyzer", analyze_articles)
    workflow.add_node("evaluator", evaluate_newsletter)
    workflow.add_node("composer", compose_newsletter)

    # Set the entry point
    workflow.set_entry_point("retriever")

    # Define the strictly linear deterministic workflow
    workflow.add_edge("retriever", "ranker")
    workflow.add_edge("ranker", "analyzer")
    workflow.add_edge("analyzer", "evaluator")
    workflow.add_edge("evaluator", "composer")
    workflow.add_edge("composer", END)

    return workflow.compile()
