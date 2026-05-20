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

load_dotenv()
logger = get_logger("analyzer")

class ArticleAnalysis(BaseModel):
    summary: str = Field(description="A concise summary of the article (maximum 2-3 sentences). Avoid repetitive phrasing.")
    why_it_matters: str = Field(description="Why this news is important for the AI industry. Be concise and high-signal.")
    tags: List[str] = Field(description="A list of 2-4 topic tags (e.g., 'AI Agents', 'Open Source', 'LLMs', 'Cybersecurity').")

def analyze_articles(state: PipelineState) -> PipelineState:
    """
    Agent responsible for analyzing and summarizing articles using Groq.
    Implements throttling, content truncation, output token optimization, and rate limit retry handling.
    Features source-aware analysis to properly differentiate news articles from GitHub repositories.
    Operates purely on the PipelineState object.
    """
    state.pipeline_stage = "analysis"
    logger.info("Analyzing articles using Groq...")
    
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
    
    # Set up structured output
    structured_llm = llm.with_structured_output(ArticleAnalysis)
    
    news_chain = news_prompt | structured_llm
    github_chain = github_prompt | structured_llm
    
    total_articles = len(state.articles)
    
    for idx, article in enumerate(state.articles, 1):
        logger.info(f"Analyzing article {idx}/{total_articles}: {article.title}")
        
        # Truncate content to optimize token usage
        truncated_content = article.content[:MAX_CONTENT_LENGTH]
        
        # Route to the appropriate processing chain
        chain = github_chain if article.source == "github" else news_chain
        
        try:
            # Implement auto-retry on rate limit errors
            retries = 0
            analysis = None
            
            while True:
                try:
                    analysis = chain.invoke({
                        "title": article.title,
                        "content": truncated_content
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
            
            # Mutate Pydantic article object in-place
            article.summary = analysis.summary
            article.why_it_matters = analysis.why_it_matters
            article.tags = analysis.tags
            
            state.metadata.total_articles_processed += 1
            
        except Exception as e:
            logger.error(f"Error analyzing article '{article.title}': {e}")
            state.errors.append(f"Analysis failed for '{article.title}': {e}")
            
            # Fallback to keep the pipeline stable
            article.summary = "Summary generation failed."
            article.why_it_matters = "Analysis failed."
            article.tags = []
            
        # Throttling sleep between articles
        if idx < total_articles:
            time.sleep(ANALYSIS_THROTTLE_SECONDS)
            
    return state
