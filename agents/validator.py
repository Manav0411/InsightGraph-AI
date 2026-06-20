import time
import os
import asyncio
from typing import List, Tuple
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from config.models import FAST_MODEL
from models.state import PipelineState, Article
from utils.logger import get_logger

logger = get_logger("validator")

class ValidationResult(BaseModel):
    is_relevant: bool = Field(description="True if the content genuinely supports and matches the title, False if it is clickbait, unrelated, or a hallucinated summary.")

async def _validate_single_article(llm: ChatGroq, article: Article, sem: asyncio.Semaphore) -> Tuple[Article, bool]:
                                                                                            
    if article.source in ["arxiv", "rss"]:
        return article, True
        
    if article.source == "hacker_news":
        prompt = (
            "You are an expert content moderator. Evaluate if the following Hacker News post "
            "is genuinely related to Artificial Intelligence, Machine Learning, or LLMs.\n\n"
            f"Title: {article.title}\n\n"
            "Use the provided tool to set is_relevant to true if it is AI-related, false otherwise."
        )
    else:
        prompt = (
            "You are an expert content moderator. Evaluate if the following article content "
            "genuinely matches its title, or if it is clickbait/unrelated noise.\n\n"
            f"Title: {article.title}\n"
            f"Content snippet (first 300 chars): {article.content[:300]}\n\n"
            "Use the provided tool to set is_relevant to true if the content is relevant, false otherwise."
        )
    
    async with sem:
        import re
        retries = 0
        while retries < 10:
            try:
                response = await llm.ainvoke(prompt)
                return article, response.is_relevant
            except Exception as e:
                err_msg = str(e)
                if "429" in err_msg or "rate_limit" in err_msg:
                    wait_match = re.search(r'Please try again in (\d+\.?\d*)s', err_msg)
                    wait_time = float(wait_match.group(1)) + 1.0 if wait_match else (5 + (2 ** retries))
                    logger.warning(f"[Validator] Rate limit hit for '{article.title}'. Waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    retries += 1
                else:
                    logger.warning(f"[Validator] Validation failed for '{article.title}', defaulting to True: {e}")
                    return article, True
                    
        logger.warning(f"[Validator] Rate limit retries exhausted for '{article.title}', defaulting to True.")
        return article, True

async def validate_articles(state: PipelineState) -> PipelineState:
    """
    Validates retrieved articles to ensure title-content relevance before downstream processing.
    Filters out noisy or unrelated articles using an ultra-fast LLM semantic check in parallel.
    """
    start_time = time.perf_counter()
    state.pipeline_stage = "validation"
    logger.info("Validating retrieved articles for grounding using FAST_MODEL...")
    
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logger.warning("No GROQ_API_KEY found, bypassing LLM validation.")
        return state
        
                                                      
    llm = ChatGroq(model=FAST_MODEL, temperature=0.0, api_key=api_key).with_structured_output(ValidationResult)
    
                                                                                                                        
    sem = asyncio.Semaphore(2)
    tasks = [_validate_single_article(llm, article, sem) for article in state.articles]
    results = await asyncio.gather(*tasks)
    
    valid_articles = []
    for article, is_relevant in results:
        if is_relevant:
            article.grounding_verified = True
            valid_articles.append(article)
        else:
            logger.warning(f"[Validator] Rejected article due to low title-content relevance: '{article.title}'")
            state.metadata.total_articles_rejected += 1
            state.metadata.validation_failures += 1
            
    total_articles = len(state.articles)
    state.articles = valid_articles
    
    elapsed_time = round(time.perf_counter() - start_time, 2)
    state.metadata.agent_timings["validator"] = elapsed_time
    
    logger.info(f"[Validator] Validated {len(valid_articles)}/{total_articles} articles.")
    logger.info(f"[Validator] Completed in {elapsed_time}s")
    
    return state
