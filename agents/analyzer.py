import os
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
    """
    print("Analyzing articles using Groq...")
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is missing. Please add it to your .env file.")
    
    # Initialize the Groq model
    # Centralized configuration prevents hardcoding and allows easy model swapping
    llm = ChatGroq(
        model=FAST_MODEL,
        temperature=0.3,
        api_key=api_key
    )
    
    # Set up structured output
    structured_llm = llm.with_structured_output(ArticleAnalysis)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert AI analyst. Given the title and content of an AI news article, provide a brief summary and explain why it matters."),
        ("human", "Title: {title}\n\nContent: {content}")
    ])
    
    chain = prompt | structured_llm
    
    analyzed_articles = []
    for article in data.get("articles", []):
        try:
            analysis = chain.invoke({
                "title": article["title"],
                "content": article["content"]
            })
            
            # Combine original article with analysis
            analyzed_article = article.copy()
            analyzed_article["summary"] = analysis.summary
            analyzed_article["why_it_matters"] = analysis.why_it_matters
            analyzed_articles.append(analyzed_article)
        except Exception as e:
            print(f"Error analyzing article '{article['title']}': {e}")
            # Fallback if parsing or API call fails
            analyzed_article = article.copy()
            analyzed_article["summary"] = "Summary generation failed."
            analyzed_article["why_it_matters"] = "Analysis failed."
            analyzed_articles.append(analyzed_article)
            
    return {"articles": analyzed_articles}
