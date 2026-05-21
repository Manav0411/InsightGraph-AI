"""
Utility for cleaning and normalizing retrieved content.
Prevents noisy multi-story blobs and unrelated content from contaminating LLM context.
"""
import re

def clean_html_noise(text: str) -> str:
    """
    Removes repetitive boilerplate, navigation text, and related story sections.
    """
    if not text:
        return ""
    
    # Remove common repetitive boilerplate phrases
    noise_patterns = [
        r"read more.*",
        r"click here to continue.*",
        r"subscribe for more.*",
        r"related stories:.*",
        r"also read:.*",
        r"share this article:.*",
        r"advertisement.*",
    ]
    
    cleaned_text = text
    for pattern in noise_patterns:
        cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE | re.MULTILINE)
        
    return cleaned_text

def normalize_content(text: str) -> str:
    """
    Normalizes whitespace and removes excessive line breaks.
    """
    if not text:
        return ""
    
    # Replace multiple newlines with a single newline
    text = re.sub(r'\n+', '\n', text)
    # Replace multiple spaces with a single space
    text = re.sub(r' +', ' ', text)
    
    return text.strip()

def truncate_content(text: str, max_length: int = 1200) -> str:
    """
    Truncates content intelligently to avoid passing massive noisy chunks to the LLM.
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
        
    return text[:max_length] + "..."
