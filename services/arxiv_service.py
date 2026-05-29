import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from utils.logger import get_logger

logger = get_logger("arxiv_service")

DEFAULT_ARXIV_QUERIES = [
    "cat:cs.AI",
    "cat:cs.CL",
    "cat:cs.LG"
]

def fetch_arxiv_papers(topics: List[str] = None, max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Fetches the latest research papers from ArXiv.
    """
    all_results = []
    
    if topics:
        # Build search query from topics. ArXiv uses 'all:keyword'
        search_query = " OR ".join([f'all:"{urllib.parse.quote(t)}"' for t in topics])
    else:
        search_query = " OR ".join(DEFAULT_ARXIV_QUERIES)
        
    encoded_query = urllib.parse.quote(search_query)
    url = f'http://export.arxiv.org/api/query?search_query={encoded_query}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}'
    
    try:
        logger.info(f"Fetching ArXiv papers with query: {search_query}")
        req = urllib.request.Request(url, headers={'User-Agent': 'InsightGraph/1.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        namespace = {'atom': 'http://www.w3.org/2005/Atom'}
        
        for entry in root.findall('atom:entry', namespace):
            title = entry.find('atom:title', namespace).text.replace('\n', ' ').strip()
            summary = entry.find('atom:summary', namespace).text.replace('\n', ' ').strip()
            pdf_url = ""
            for link in entry.findall('atom:link', namespace):
                if link.attrib.get('title') == 'pdf':
                    pdf_url = link.attrib.get('href')
                    break
            if not pdf_url:
                pdf_url = entry.find('atom:id', namespace).text
                
            all_results.append({
                "title": title,
                "url": pdf_url,
                "content": f"Abstract: {summary}",
                "image_url": None,
                "source": "arxiv"
            })
            
        logger.info(f"Retrieved {len(all_results)} papers from ArXiv.")
        
    except Exception as e:
        logger.error(f"Error fetching from ArXiv: {e}")
        
    return all_results
