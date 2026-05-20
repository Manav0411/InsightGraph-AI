import os
import time
from typing import Dict, Any, List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from config.models import FAST_MODEL

load_dotenv()

class ArticleAnalysis(BaseModel):
    summary: str = Field(description="A concise summary of the article.")
    why_it_matters: str = Field(description="Why this news is important for the AI industry.")

def analyze_articles(data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Agent responsible for analyzing and summarizing articles using Groq.
    Implements throttling, content truncation, output token optimization, and rate limit retry handling.
    """
    print("Analyzing articles using Groq...")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is missing. Please add it to your .env file.")
    
    # Initialize the Groq model with optimized max_tokens limit of 250
    llm = ChatGroq(
        model=FAST_MODEL,
        temperature=0.3,
        max_tokens=250,
        api_key=api_key
    )
    
    # Set up structured output
    structured_llm = llm.with_structured_output(ArticleAnalysis)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert AI analyst. Given the title and content of an AI news article, provide a brief summary and explain why it matters."),
        ("human", "Title: {title}\n\nContent: {content}")
    ])
    
    chain = prompt | structured_llm
    
    articles = data.get("articles", [])
    total_articles = len(articles)
    analyzed_articles = []
    
    for idx, article in enumerate(articles, 1):
        print(f"Analyzing article {idx}/{total_articles}...")
        
        # Truncate content to 2000 characters to optimize token usage
        content = article.get("content", "")
        truncated_content = content[:2000]
        
        try:
            # Implement auto-retry on 429 rate limit errors
            retries = 0
            analysis = None
            
            while True:
                try:
                    analysis = chain.invoke({
                        "title": article.get("title", ""),
                        "content": truncated_content
                    })
                    break  # Succeeded, break retry loop
                except Exception as e:
                    err_msg = str(e)
                    # Check if error is related to rate limiting (HTTP 429)
                    is_rate_limit = "429" in err_msg or "rate_limit" in err_msg or (hasattr(e, "status_code") and e.status_code == 429)
                    
                    if is_rate_limit:
                        print("Retrying after rate limit...")
                        time.sleep(8)
                        retries += 1
                        if retries >= 5:  # Break out if rate limit persists after 5 attempts
                            raise TimeoutError(f"Rate limit retry threshold exceeded for article: {article.get('title')}")
                    else:
                        raise e  # Propagate other exceptions to be caught by outer try-except block
            
            # Combine original article with successfully generated analysis
            analyzed_article = article.copy()
            analyzed_article["summary"] = analysis.summary
            analyzed_article["why_it_matters"] = analysis.why_it_matters
            analyzed_articles.append(analyzed_article)
            
        except Exception as e:
            print(f"Error analyzing article '{article.get('title', '')}': {e}")
            # Fallback to keep the pipeline stable even if this individual article fails
            analyzed_article = article.copy()
            analyzed_article["summary"] = "Summary generation failed."
            analyzed_article["why_it_matters"] = "Analysis failed."
            analyzed_articles.append(analyzed_article)
            
        # Throttling sleep of 2 seconds between articles to prevent rate limit triggers
        if idx < total_articles:
            time.sleep(2)
            
    return {"articles": analyzed_articles}
