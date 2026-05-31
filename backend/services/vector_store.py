import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.db.database import SessionLocal
from backend.models.db_article import Article
from backend.models.db_briefing import Briefing
from utils.logger import get_logger

# Import SentenceTransformer directly
from sentence_transformers import SentenceTransformer

logger = get_logger("vector_store")

class VectorMemoryManager:
    """
    Manages longitudinal memory using pgvector and SentenceTransformer.
    """
    def __init__(self):
        # Use a lightweight local embedding model. 
        # This will download the model weights (~90MB) on the very first run.
        try:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            logger.info("[VectorStore] Initialized SentenceTransformer model.")
        except Exception as e:
            logger.error(f"[VectorStore] Failed to initialize SentenceTransformer: {e}")
            raise

    def store_briefing(self, briefing: Briefing) -> int:
        """
        Embeds and stores all articles from a finalized briefing into the PostgreSQL vector store.
        Returns the number of articles successfully stored.
        """
        if not briefing.articles:
            return 0
            
        success_count = 0
        
        with SessionLocal() as db:
            for article in briefing.articles:
                try:
                    # We construct a composite text block for maximum semantic capture
                    composite_text = f"Title: {article.title}\nSource: {article.source}\nSummary: {article.summary}\nWhy It Matters: {article.why_it_matters}"
                    
                    # Compute embedding
                    embedding = self.model.encode(composite_text).tolist()
                    
                    # Update the article in the database
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
        """
        Searches the PostgreSQL vector store for past articles semantically similar to the query.
        Limits results to articles owned by the specified user.
        """
        try:
            query_embedding = self.model.encode(query_text).tolist()
            
            with SessionLocal() as db:
                # Fetch articles belonging to user's briefings, order by L2 distance
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

# Singleton instance for easy import across the app
memory_manager = VectorMemoryManager()
