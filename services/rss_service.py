import urllib.request
import xml.etree.ElementTree as ET
import datetime
from email.utils import parsedate_to_datetime
from typing import List, Dict, Any
from utils.logger import get_logger
from utils.image_utils import extract_og_image

logger = get_logger("rss_service")

                       
RSS_FEEDS = {
    "Hugging Face": "https://huggingface.co/blog/feed.xml",
    "VentureBeat AI": "https://venturebeat.com/category/ai/feed/",
    "MIT Technology Review AI": "https://technologyreview.com/feed/"
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 InsightGraph/1.0'
}

def fetch_rss_feeds(max_per_feed: int = 3) -> List[Dict[str, Any]]:
    """
    Fetches the latest official announcements from major AI lab RSS feeds.
    Uses basic XML parsing.
    """
    all_results = []
    
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            logger.info(f"Fetching RSS feed from {source_name}: {feed_url}")
            req = urllib.request.Request(feed_url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=10) as response:
                xml_data = response.read()
                
            root = ET.fromstring(xml_data)
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            
                                                     
            items = root.findall('.//item')
            if not items:
                                         
                items = root.findall('.//atom:entry', namespace)
                
            feed_articles = []
            
            for item in items:
                                     
                title_elem = item.find('title')
                link_elem = item.find('link')
                desc_elem = item.find('description')
                pub_date = item.findtext('pubDate')
                
                dt = None
                if pub_date:
                    try:
                        dt = parsedate_to_datetime(pub_date)
                        now = datetime.datetime.now(datetime.timezone.utc)
                        if (now - dt).days > 7:
                            continue                    
                    except Exception:
                        pass                                      
                        
                                         
                if title_elem is None:
                    title_elem = item.find('atom:title', namespace)
                if desc_elem is None:
                    desc_elem = item.find('atom:summary', namespace)
                    if desc_elem is None:
                        desc_elem = item.find('atom:content', namespace)
                
                title = title_elem.text.strip() if title_elem is not None and title_elem.text else "Untitled"
                
                link = ""
                if link_elem is not None:
                    if link_elem.text:
                        link = link_elem.text.strip()
                    elif link_elem.attrib.get('href'):
                        link = link_elem.attrib.get('href')
                        
                description = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""
                
                                                  
                import re
                description = re.sub(r'<[^>]+>', ' ', description).strip()
                
                if title and link:
                    feed_articles.append({
                        "title": f"[{source_name}] {title}",
                        "url": link,
                        "content": description,
                        "image_url": extract_og_image(link),
                        "source": "rss",
                        "_dt": dt
                    })
                    
                                                
            feed_articles.sort(key=lambda x: x.get("_dt") or datetime.datetime.min.replace(tzinfo=datetime.timezone.utc), reverse=True)
            
                                                                      
            for article in feed_articles[:max_per_feed]:
                article.pop("_dt", None)
                all_results.append(article)
                    
        except Exception as e:
            logger.error(f"Error fetching RSS from {source_name}: {e}")
            
    logger.info(f"Retrieved {len(all_results)} official announcements via RSS.")
    return all_results
