from typing import Dict, Any, List

def evaluate_newsletter(data: Dict[str, List[Dict[str, Any]]]) -> bool:
    """
    Agent responsible for basic validation of the articles and summaries.
    """
    print("Evaluating generated content...")
    articles = data.get("articles", [])
    
    if not articles:
        print("Evaluation failed: No articles provided.")
        return False
        
    seen_titles = set()
    
    for article in articles:
        title = article.get("title", "")
        summary = article.get("summary", "")
        
        # Check for empty summaries
        if not summary or summary == "Summary generation failed.":
            print(f"Evaluation Warning: Article '{title}' has an invalid summary.")
            
        # Check for duplicate titles
        if title in seen_titles:
            print(f"Evaluation Warning: Duplicate article found '{title}'.")
        seen_titles.add(title)
        
    print("Evaluation completed.")
    return True
