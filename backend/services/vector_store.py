import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.db.database import SessionLocal
from backend.models.db_article import Article
from backend.models.db_briefing import Briefing
from utils.logger import get_logger

import requests
from huggingface_hub import InferenceClient

logger = get_logger("vector_store")

class VectorMemoryManager:
    def __init__(self):
        self.model = "sentence-transformers/all-MiniLM-L6-v2"
        hf_token = os.getenv("HF_TOKEN")
        self.client = InferenceClient(api_key=hf_token) if hf_token else None
        logger.info("[VectorStore] Initialized VectorMemoryManager to use Hugging Face InferenceClient API.")

    def _get_embedding(self, text: str) -> List[float]:
        if not self.client:
            raise Exception("HF_TOKEN is not set.")
            
        try:
            result = self.client.feature_extraction(
                text,
                model=self.model,
            )
            
            # The result from feature_extraction is a numpy array
            if hasattr(result, "tolist"):
                return result.tolist()
            elif isinstance(result, list):
                return result
            else:
                raise Exception("Unexpected HF Hub response format")
                
        except Exception as e:
            raise Exception(f"HF Hub Inference Failed: {str(e)}")

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
                    logger.warning(f"[VectorStore] Skipped embedding for article {article.id} (Known Cloud Block): {e}")
            
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
            logger.warning(f"[VectorStore] Skipped historical query (Known Cloud Block): {str(e)}")
            return []

memory_manager = VectorMemoryManager()
