import os
import time
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
from config.models import FAST_MODEL
from config.settings import MAX_OUTPUT_TOKENS, RETRY_DELAY_SECONDS, MAX_RETRIES, ANALYSIS_THROTTLE_SECONDS, MAX_CONTENT_LENGTH
from utils.logger import get_logger
from models.state import PipelineState
from prompts.news_analysis_prompt import news_prompt
from prompts.github_analysis_prompt import github_prompt
from backend.services.vector_store import memory_manager

load_dotenv()
logger = get_logger("analyzer")

class ArticleAnalysis(BaseModel):
    summary: str = Field(description="A concise summary of the article (maximum 2-3 sentences). Avoid repetitive phrasing.")
    details: List[str] = Field(description="Extract 3-5 complete, full-sentence concrete bullet points containing the most important details, facts, or technical specs. Do NOT just output short keywords or tags.")
    why_it_matters: str = Field(description="Why this news is important for the AI industry. Be concise and high-signal.")
    tags: List[str] = Field(description="A list of 2-4 topic tags (e.g., 'Model Architecture', 'Funding', 'Regulation', 'Cybersecurity').")

def analyze_articles(state: PipelineState) -> PipelineState:
    """
    Agent responsible for analyzing each retrieved article using the Groq API.
    Features source-aware analysis to properly differentiate news articles from GitHub repositories.
    Operates purely on the PipelineState object.
    """
    start_time = time.perf_counter()
    
    # Detect analyzer self-retry transition
    if state.pipeline_stage == "analysis":
        state.analyzer_retry_count += 1
        state.metadata.recovery_attempts += 1
        state.metadata.conditional_routes_triggered += 1
        logger.warning(
            f"[Graph] Routing from Analyzer → Analyzer (Retry). "
            f"Retry Count: {state.analyzer_retry_count}/1"
        )
        # Clear out previous analyzer errors so they don't compound
        state.errors = [e for e in state.errors if not ("Analysis failed" in e or "analyzer" in e.lower())]
        state.warnings = [w for w in state.warnings if not ("Analysis failed" in w or "analyzer" in w.lower())]
        
    state.pipeline_stage = "analysis"
    logger.info("Analyzing articles using Groq...")
    logger.info("[Analyzer] Using grounded summarization mode")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        error_msg = "GROQ_API_KEY environment variable is missing."
        logger.error(error_msg)
        state.errors.append(error_msg)
        return state
    
    # Initialize the Groq model
    llm = ChatGroq(
        model=FAST_MODEL,
        temperature=0.3,
        max_tokens=MAX_OUTPUT_TOKENS,
        api_key=api_key
    )
    
    # Set up structured output with include_raw=True to capture token usage metadata
    structured_llm = llm.with_structured_output(ArticleAnalysis, include_raw=True)
    
    news_chain = news_prompt | structured_llm
    github_chain = github_prompt | structured_llm
    
    # Reset processed count at the start of analysis to prevent double counting on retries
    state.metadata.total_articles_processed = 0
    
    total_articles = len(state.articles)
    
    for idx, article in enumerate(state.articles, 1):
        # Skip if already successfully analyzed in a previous attempt
        if article.summary and article.summary != "Summary generation failed.":
            logger.info(f"Skipping already-analyzed article {idx}/{total_articles}: {article.title}")
            state.metadata.total_articles_processed += 1
            continue
            
        logger.info(f"Analyzing article {idx}/{total_articles}: {article.title}")
        
        # Truncate content to MAX_CONTENT_LENGTH to reduce context noise and prevent topic contamination
        truncated_content = article.content[:MAX_CONTENT_LENGTH]
        
        # Route to the appropriate processing chain
        chain = github_chain if article.source == "github" else news_chain
        
        # 1. Retrieve Historical Context from Vector Memory
        history_results = memory_manager.get_historical_context(article.title, state.user_profile.user_id)
        history_str = "No historical context available."
        
        if history_results:
            logger.info(f"[Analyzer] Found {len(history_results)} related historical articles for: {article.title}")
            history_str = ""
            for h in history_results:
                date_str = h['generated_at'][:10] if h.get('generated_at') else "Unknown Date"
                history_str += f"- [{date_str}] {h['title']}: {h['content'][:300]}...\n"
        
        try:
            # Implement auto-retry on rate limit errors
            retries = 0
            analysis_dict = None
            
            while True:
                try:
                    analysis_dict = chain.invoke({
                        "title": article.title,
                        "content": truncated_content,
                        "history": history_str
                    })
                    break  # Succeeded, break retry loop
                except Exception as e:
                    err_msg = str(e)
                    is_rate_limit = "429" in err_msg or "rate_limit" in err_msg or (hasattr(e, "status_code") and e.status_code == 429)
                    
                    if is_rate_limit:
                        logger.warning(f"Rate limit hit. Retrying in {RETRY_DELAY_SECONDS}s...")
                        time.sleep(RETRY_DELAY_SECONDS)
                        retries += 1
                        if retries >= MAX_RETRIES:
                            raise TimeoutError(f"Rate limit retry threshold exceeded for article: {article.title}")
                    else:
                        raise e
            
            # Extract structured response and raw token usage
            analysis = analysis_dict.get("parsed")
            raw_msg = analysis_dict.get("raw")
            
            if raw_msg and hasattr(raw_msg, "response_metadata"):
                token_usage = raw_msg.response_metadata.get("token_usage", {})
                state.metadata.total_prompt_tokens += token_usage.get("prompt_tokens", 0)
                state.metadata.total_completion_tokens += token_usage.get("completion_tokens", 0)
            
            # Mutate Pydantic article object in-place
            if analysis:
                article.summary = analysis.summary
                article.details = analysis.details
                article.why_it_matters = analysis.why_it_matters
                article.tags = analysis.tags
            
            state.metadata.total_articles_processed += 1
            
        except Exception as e:
            logger.error(f"Error analyzing article '{article.title}': {e}")
            state.errors.append(f"Analysis failed for '{article.title}': {e}")
            
            # Fallback to keep the pipeline stable
            article.summary = "Summary generation failed."
            article.details = []
            article.why_it_matters = "Analysis failed."
            article.tags = []
            
        # Throttling sleep between articles
        if idx < total_articles:
            time.sleep(ANALYSIS_THROTTLE_SECONDS)
            
    elapsed_time = round(time.perf_counter() - start_time, 2)
    state.metadata.agent_timings["analyzer"] = elapsed_time
    logger.info(f"[Analyzer] Completed in {elapsed_time}s")
            
    return state
