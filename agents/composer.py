import os
from typing import Dict, Any, List

def compose_newsletter(data: Dict[str, List[Dict[str, Any]]]) -> str:
    """
    Agent responsible for formatting the analyzed articles into a Markdown newsletter.
    """
    print("Composing newsletter...")
    articles = data.get("articles", [])
    
    markdown_content = "# AI Daily Digest\n\n## Top Stories\n\n"
    
    for i, article in enumerate(articles, 1):
        title = article.get("title", "Untitled")
        url = article.get("url", "#")
        summary = article.get("summary", "No summary available.")
        why_it_matters = article.get("why_it_matters", "No analysis available.")
        
        markdown_content += f"### {i}. [{title}]({url})\n"
        markdown_content += f"**Summary:** {summary}\n\n"
        markdown_content += f"**Why it matters:** {why_it_matters}\n\n"
        markdown_content += "---\n\n"
        
    return markdown_content

def save_newsletter(markdown_content: str, filepath: str = "output/newsletter.md"):
    """
    Saves the generated markdown to a file.
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown_content)
