import os
import time
from models.state import PipelineState
from utils.logger import get_logger
from langchain_groq import ChatGroq
from config.models import REASONING_MODEL

logger = get_logger("composer")

def compose_newsletter(state: PipelineState) -> PipelineState:
    """
    Agent responsible for formatting the analyzed articles into a Markdown newsletter.
    Organizes by source and sorts by trend score for maximum readability.
    This is the ONLY layer responsible for markdown generation.
    """
    start_time = time.perf_counter()
    state.pipeline_stage = "composition"
    logger.info("Composing newsletter...")
    
    # Sort articles by trend score globally before segmenting
    articles = sorted(state.articles, key=lambda x: x.trend_score, reverse=True)
    
    tavily_articles = [a for a in articles if a.source == "tavily"]
    github_articles = [a for a in articles if a.source == "github"]
    
    markdown_content = "# InsightGraph Digest\n> Adaptive AI Intelligence Platform\n\n"
    if state.user_profile:
        email_str = f" ({state.user_profile.email})" if state.user_profile.email else ""
        markdown_content += f"*Personalized for **{state.user_profile.user_id}**{email_str}*\n\n"
    else:
        markdown_content += "\n"
        
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key and articles:
        try:
            logger.info("Generating editorial intro with REASONING_MODEL...")
            llm = ChatGroq(model=REASONING_MODEL, temperature=0.5, max_tokens=256, api_key=api_key)
            top_context = "\n".join([f"- {a.title}: {a.summary}" for a in articles[:3]])
            prompt = (
                "You are the editor of an elite AI intelligence briefing. Write a 2-3 sentence engaging, "
                "professional editorial introduction summarizing the overarching theme of these top stories:\n"
                f"{top_context}\n\nDo not use generic buzzwords. Write directly to the reader. Do not start with greetings like 'Welcome'."
            )
            response = llm.invoke(prompt)
            markdown_content += f"*{response.content.strip()}*\n\n---\n\n"
        except Exception as e:
            logger.warning(f"Failed to generate editorial intro: {e}")
        
    # Recommended For You section (top 3 articles with personalization_boost > 0)
    boosted_articles = [a for a in articles if getattr(a, "personalization_boost", 0.0) > 0.0]
    boosted_articles = sorted(boosted_articles, key=lambda x: (x.personalization_boost, x.trend_score), reverse=True)
    recommended_articles = boosted_articles[:3]
    
    if recommended_articles:
        markdown_content += "## Recommended For You\n\n"
        for i, article in enumerate(recommended_articles, 1):
            title = article.title
            url = article.url
            summary = article.summary or "No summary available."
            why_it_matters = article.why_it_matters or "No analysis available."
            source = article.source.capitalize()
            trend_score = article.trend_score
            boost = article.personalization_boost
            tags = ", ".join(article.tags)
            
            stars_part = f" (⭐ {article.stars})" if (article.source == "github" and article.stars) else ""
            
            markdown_content += f"### {i}. [{title}]({url}){stars_part}\n"
            markdown_content += f"**Trend Score:** {trend_score} *(Personalization Boost: +{boost})*\n"
            markdown_content += f"**Source:** {source}\n"
            if tags:
                markdown_content += f"**Tags:** {tags}\n"
            markdown_content += f"\n**Summary:** {summary}\n\n"
            markdown_content += f"**Why it matters:** {why_it_matters}\n\n"
            markdown_content += "---\n\n"
            
    if tavily_articles:
        markdown_content += "## Top Stories\n\n"
        for i, article in enumerate(tavily_articles, 1):
            title = article.title
            url = article.url
            summary = article.summary or "No summary available."
            why_it_matters = article.why_it_matters or "No analysis available."
            source = article.source.capitalize()
            trend_score = article.trend_score
            tags = ", ".join(article.tags)
            
            markdown_content += f"### {i}. [{title}]({url})\n"
            markdown_content += f"**Trend Score:** {trend_score}\n"
            markdown_content += f"**Source:** {source}\n"
            if tags:
                markdown_content += f"**Tags:** {tags}\n"
            markdown_content += f"\n**Summary:** {summary}\n\n"
            markdown_content += f"**Why it matters:** {why_it_matters}\n\n"
            markdown_content += "---\n\n"
            
    if github_articles:
        markdown_content += "## Trending Open Source AI Projects\n\n"
        for i, article in enumerate(github_articles, 1):
            title = article.title
            url = article.url
            summary = article.summary or "No summary available."
            why_it_matters = article.why_it_matters or "No analysis available."
            source = article.source.capitalize()
            stars = article.stars or 0
            trend_score = article.trend_score
            tags = ", ".join(article.tags)
            
            star_label = f" (⭐ {stars})" if stars else ""
            markdown_content += f"### {i}. [{title}]({url}){star_label}\n"
            markdown_content += f"**Trend Score:** {trend_score}\n"
            markdown_content += f"**Source:** {source}\n"
            if tags:
                markdown_content += f"**Tags:** {tags}\n"
            markdown_content += f"\n**Summary:** {summary}\n\n"
            markdown_content += f"**Why it matters:** {why_it_matters}\n\n"
            markdown_content += "---\n\n"
            
    elapsed_time = round(time.perf_counter() - start_time, 2)
    state.metadata.agent_timings["composer"] = elapsed_time
    logger.info(f"[Composer] Completed in {elapsed_time}s")
            
    state.final_newsletter = markdown_content
    return state


def save_newsletter(markdown_content: str, filepath: str = "output/newsletter.md"):
    """
    Saves the generated markdown to a file.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(markdown_content)
