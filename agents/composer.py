import os
from models.state import PipelineState
from utils.logger import get_logger

logger = get_logger("composer")

def compose_newsletter(state: PipelineState) -> str:
    """
    Agent responsible for formatting the analyzed articles into a Markdown newsletter.
    Organizes by source and sorts by trend score for maximum readability.
    This is the ONLY layer responsible for markdown generation.
    """
    state.pipeline_stage = "composition"
    logger.info("Composing newsletter...")
    
    # Sort articles by trend score globally before segmenting
    articles = sorted(state.articles, key=lambda x: x.trend_score, reverse=True)
    
    tavily_articles = [a for a in articles if a.source == "tavily"]
    github_articles = [a for a in articles if a.source == "github"]
    
    markdown_content = "# AI Trend Intelligence Digest\n\n"
    
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
            
    return markdown_content

def save_newsletter(markdown_content: str, filepath: str = "output/newsletter.md"):
    """
    Saves the generated markdown to a file.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(markdown_content)
