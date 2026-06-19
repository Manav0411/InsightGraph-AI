import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.db.database import SessionLocal
from backend.models.db_article import Article
from backend.models.db_briefing import Briefing
from utils.logger import get_logger

import requests

logger = get_logger("vector_store")

class VectorMemoryManager:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
        logger.info("[VectorStore] Initialized VectorMemoryManager to use Hugging Face Inference API.")

    def _get_embedding(self, text: str) -> List[float]:
        headers = {}
        hf_token = os.getenv("HF_TOKEN")
        if hf_token:
            headers["Authorization"] = f"Bearer {hf_token}"
            
        response = requests.post(self.api_url, headers=headers, json={"inputs": [text]})
        
        if response.status_code != 200:
            raise Exception(f"HF API Error: {response.status_code} - {response.text}")
            
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        else:
            raise Exception(f"Unexpected HF API response format")

    def store_briefing(self, briefing: Briefing) -> int:
        if not briefing.articles:
            return 0
            
        success_count = 0
        
        with SessionLocal() as db:
            for article in briefing.articles:
                try:
                    composite_text = f"Title: {article.title}\nSource: {article.source}\nSummary: {article.summary}\nWhy It Matters: {article.why_it_matters}"
                    embedding = self._get_embedding(composite_text)
                    db.query(Article).filter(Article.id == article.id).update({"embedding": embedding})
                    success_count += 1
                except Exception as e:
                    logger.error(f"[VectorStore] Failed to compute/store embedding for article {article.id}: {e}")
            
            try:
                db.commit()
                logger.info(f"[VectorStore] Successfully indexed {success_count} articles from briefing {briefing.id}.")
            except Exception as e:
                db.rollback()
                logger.error(f"[VectorStore] Failed to commit embeddings for briefing {briefing.id}: {e}")
                return 0
                
        return success_count

    def get_historical_context(self, query_text: str, user_id: str, limit: int = 2) -> List[Dict[str, Any]]:
        try:
            query_embedding = self._get_embedding(query_text)
            
            with SessionLocal() as db:
                results = db.query(Article, Article.embedding.l2_distance(query_embedding).label('distance')) \
                    .join(Briefing) \
                    .filter(Briefing.user_id == user_id) \
                    .filter(Article.embedding.isnot(None)) \
                    .order_by('distance') \
                    .limit(limit) \
                    .all()
                    
                formatted_results = []
                for article, distance in results:
                    composite_text = f"Title: {article.title}\nSource: {article.source}\nSummary: {article.summary}\nWhy It Matters: {article.why_it_matters}"
                    
                    formatted_results.append({
                        "id": article.id,
                        "title": article.title,
                        "source": article.source,
                        "url": article.url,
                        "generated_at": article.briefing.generated_at.isoformat() if article.briefing else None,
                        "distance": float(distance),
                        "content": composite_text
                    })
                    
                return formatted_results
                
        except Exception as e:
            logger.error(f"[VectorStore] Query failed for text '{query_text[:30]}...': {str(e)}")
            return []

memory_manager = VectorMemoryManager()
