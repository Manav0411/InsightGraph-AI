import os
import time
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from typing import List
from dotenv import load_dotenv
from config.models import REASONING_MODEL, FAST_MODEL
from config.settings import MAX_OUTPUT_TOKENS, RETRY_DELAY_SECONDS, MAX_RETRIES, ANALYSIS_THROTTLE_SECONDS, MAX_CONTENT_LENGTH
from utils.logger import get_logger
from models.state import PipelineState
from prompts.news_analysis_prompt import news_prompt
from prompts.arxiv_analysis_prompt import arxiv_prompt
from prompts.community_analysis_prompt import community_prompt
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

    state.pipeline_stage = "analysis"
    logger.info("Analyzing articles using Groq...")
    logger.info("[Analyzer] Using grounded summarization mode")
    
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        error_msg = "GROQ_API_KEY environment variable is missing."
        logger.error(error_msg)
        state.errors.append(error_msg)
        return state
    
                                
    reasoning_llm = ChatGroq(
        model=REASONING_MODEL,
        temperature=0.0,
        max_tokens=MAX_OUTPUT_TOKENS,
        api_key=api_key
    )
    fast_llm = ChatGroq(
        model=FAST_MODEL,
        temperature=0.0,
        max_tokens=MAX_OUTPUT_TOKENS,
        api_key=api_key
    )
    
    # Groq's native Structured Output API (method="json_schema") is supported for
    # openai/gpt-oss and guarantees schema-valid JSON. The old function_calling
    # path produced malformed tool-call args on gpt-oss.
    structured_reasoning = reasoning_llm.with_structured_output(
        ArticleAnalysis, method="json_schema", include_raw=True
    )
    structured_fast = fast_llm.with_structured_output(
        ArticleAnalysis, method="json_schema", include_raw=True
    )
    
    news_chain = news_prompt | structured_fast
    arxiv_chain = arxiv_prompt | structured_reasoning
    community_chain = community_prompt | structured_fast
    
                                                                                          
    state.metadata.total_articles_processed = 0
    
    total_articles = len(state.articles)
    
    for idx, article in enumerate(state.articles, 1):
                                                                     
        if article.summary and article.summary != "Summary generation failed.":
            logger.info(f"Skipping already-analyzed article {idx}/{total_articles}: {article.title}")
            state.metadata.total_articles_processed += 1
            continue
            
        logger.info(f"Analyzing article {idx}/{total_articles}: {article.title}")
        
                                                                                                        
        truncated_content = article.content[:MAX_CONTENT_LENGTH]
        
                                                   
        if article.source == "arxiv":
            chain = arxiv_chain
        elif article.source == "hacker_news":
            chain = community_chain
        else:
            chain = news_chain
        
                                                           
        history_results = memory_manager.get_historical_context(article.title, state.user_profile.user_id)
        history_str = "No historical context available."
        
        if history_results:
            logger.info(f"[Analyzer] Found {len(history_results)} related historical articles for: {article.title}")
            history_str = ""
            for h in history_results:
                date_str = h['generated_at'][:10] if h.get('generated_at') else "Unknown Date"
                history_str += f"- [{date_str}] {h['title']}: {h['content'][:300]}...\n"
        
        try:
            import re
            retries = 0
            analysis_dict = None
            used_fast_fallback = (chain is news_chain or chain is community_chain)

            while True:
                try:
                    analysis_dict = chain.invoke({
                        "title": article.title,
                        "content": truncated_content,
                        "history": history_str
                    })
                    break
                except Exception as e:
                    err_msg = str(e)
                    is_rate_limit = "429" in err_msg or "rate_limit" in err_msg or (hasattr(e, "status_code") and e.status_code == 429)
                    if not is_rate_limit:
                        raise e

                    wait_match = re.search(r'try again in (\d+\.?\d*)s', err_msg)
                    if wait_match:
                        wait_time = min(float(wait_match.group(1)) + 1.0, 30.0)
                        retries += 1
                        if retries >= MAX_RETRIES:
                            raise TimeoutError(f"Rate limit retry threshold exceeded for article: {article.title}")
                        logger.warning(f"Rate limit hit. Waiting {wait_time}s (retry {retries}/{MAX_RETRIES})...")
                        time.sleep(wait_time)
                        continue

                    # No wait time returned -> daily-token (TPD) style limit.
                    if used_fast_fallback:
                        # Already on the cheap model and still limited: give up on this
                        # article rather than hammering the API in a tight loop.
                        raise TimeoutError(f"Token limit reached; skipping analysis for: {article.title}")

                    logger.warning(f"Token limit on REASONING_MODEL. Falling back to FAST_MODEL for: {article.title}")
                    fallback_llm = ChatGroq(
                        model=FAST_MODEL,
                        temperature=0.0,
                        max_tokens=MAX_OUTPUT_TOKENS,
                        api_key=api_key
                    )
                    structured_fallback_llm = fallback_llm.with_structured_output(
                        ArticleAnalysis, method="json_schema", include_raw=True
                    )
                    if article.source == "arxiv":
                        chain = arxiv_prompt | structured_fallback_llm
                    elif article.source == "hacker_news":
                        chain = community_prompt | structured_fallback_llm
                    else:
                        chain = news_prompt | structured_fallback_llm
                    used_fast_fallback = True
                    continue
            
                                                             
            analysis = analysis_dict.get("parsed")
            raw_msg = analysis_dict.get("raw")
            
            if raw_msg and hasattr(raw_msg, "response_metadata"):
                token_usage = raw_msg.response_metadata.get("token_usage", {})
                state.metadata.total_prompt_tokens += token_usage.get("prompt_tokens", 0)
                state.metadata.total_completion_tokens += token_usage.get("completion_tokens", 0)
            
                                                     
            if analysis:
                article.summary = analysis.summary
                article.details = analysis.details
                article.why_it_matters = analysis.why_it_matters
                article.tags = analysis.tags
            
            state.metadata.total_articles_processed += 1
            
        except Exception as e:
            err_msg = str(e)
            salvaged = False
            
            if "failed_generation" in err_msg and "<function=ArticleAnalysis>" in err_msg:
                try:
                    import re, json
                                                                         
                    match = re.search(r"<function=ArticleAnalysis>\s*(\{.*\})", err_msg, re.DOTALL)
                    if match:
                        json_str = match.group(1)
                                                                                                  
                        json_str = json_str.replace("\\'", "'")
                                                                                              
                        for i in range(len(json_str), 0, -1):
                            try:
                                parsed = json.loads(json_str[:i], strict=False)
                                article.summary = parsed.get("summary", "Summary salvaged.")
                                article.details = parsed.get("details", [])
                                article.why_it_matters = parsed.get("why_it_matters", "Salvaged.")
                                article.tags = parsed.get("tags", [])
                                salvaged = True
                                logger.info(f"Successfully salvaged failed generation for '{article.title}'")
                                state.metadata.total_articles_processed += 1
                                break
                            except json.JSONDecodeError:
                                continue
                except Exception as parse_err:
                    logger.warning(f"Failed to salvage: {parse_err}")
            
            if not salvaged:
                if "Token limit reached" in err_msg:
                    logger.warning(f"[Analyzer] Skipped '{article.title}' - Groq daily token limit reached.")
                    state.metadata.token_limit_hit = True
                elif "Rate limit retry threshold" in err_msg:
                    logger.warning(f"[Analyzer] Skipped '{article.title}' - rate-limit retries exhausted.")
                else:
                    logger.warning(f"[Analyzer] Failed to analyze '{article.title}': {e}")

                # Mark as failed so the evaluator prunes it.
                article.summary = "Summary generation failed."
                article.details = []
                article.why_it_matters = "Analysis failed."
                article.tags = []
            
                                           
        if idx < total_articles:
            time.sleep(ANALYSIS_THROTTLE_SECONDS)
            
    elapsed_time = round(time.perf_counter() - start_time, 2)
    state.metadata.agent_timings["analyzer"] = elapsed_time
    logger.info(f"[Analyzer] Completed in {elapsed_time}s")
            
    return state
