import os
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from backend.models.db_briefing import Briefing
from backend.schemas.responses import ArticleResponse
from utils.logger import get_logger

logger = get_logger("vector_store")

# Define paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHROMA_DB_DIR = os.path.join(BASE_DIR, ".chroma_db")

class VectorMemoryManager:
    """
    Manages longitudinal memory using ChromaDB.
    """
    def __init__(self):
        # Initialize persistent client
        self.client = chromadb.PersistentClient(
            path=CHROMA_DB_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Use a lightweight local embedding model. 
        # This will download the model weights (~90MB) on the very first run.
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Create or get the collection
        self.collection = self.client.get_or_create_collection(
            name="insightgraph_memory",
            embedding_function=self.embedding_function,
            metadata={"description": "Long-term agentic memory of all finalized articles"}
        )
        logger.info(f"[VectorStore] Initialized. Collection currently holds {self.collection.count()} articles.")

    def store_briefing(self, briefing: Briefing) -> int:
        """
        Embeds and stores all articles from a finalized briefing into the vector store.
        Returns the number of articles successfully stored.
        """
        if not briefing.articles:
            return 0
            
        ids = []
        documents = []
        metadatas = []
        
        for article in briefing.articles:
            # We construct a composite text block for maximum semantic capture
            composite_text = f"Title: {article.title}\nSource: {article.source}\nSummary: {article.summary}\nWhy It Matters: {article.why_it_matters}"
            
            # Use the article's database UUID as the Chroma document ID
            doc_id = str(article.id)
            
            # Store metadata for filtering and citation
            metadata = {
                "briefing_id": str(briefing.id),
                "user_id": str(briefing.user_id),
                "title": article.title,
                "url": article.url,
                "source": article.source,
                "trend_score": float(article.trend_score),
                "generated_at": briefing.generated_at.isoformat()
            }
            
            ids.append(doc_id)
            documents.append(composite_text)
            metadatas.append(metadata)
            
        try:
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            logger.info(f"[VectorStore] Successfully indexed {len(ids)} articles from briefing {briefing.id}.")
            return len(ids)
        except Exception as e:
            logger.error(f"[VectorStore] Failed to index briefing {briefing.id}: {str(e)}")
            return 0

    def get_historical_context(self, query_text: str, user_id: str, limit: int = 2) -> List[Dict[str, Any]]:
        """
        Searches the vector store for past articles semantically similar to the query.
        Limits results to articles owned by the specified user.
        """
        try:
            # Filter by user_id to ensure strict privacy boundaries
            results = self.collection.query(
                query_texts=[query_text],
                n_results=limit,
                where={"user_id": user_id}
            )
            
            formatted_results = []
            
            # ChromaDB returns parallel arrays. We check if there are any matches.
            if not results["ids"] or not results["ids"][0]:
                return formatted_results
                
            for idx in range(len(results["ids"][0])):
                doc_id = results["ids"][0][idx]
                document = results["documents"][0][idx]
                metadata = results["metadatas"][0][idx]
                distance = results["distances"][0][idx]
                
                # A lower distance means higher similarity. We can set a threshold if needed.
                # For MiniLM, distances are typically L2 distance.
                
                formatted_results.append({
                    "id": doc_id,
                    "title": metadata.get("title"),
                    "source": metadata.get("source"),
                    "url": metadata.get("url"),
                    "generated_at": metadata.get("generated_at"),
                    "distance": distance,
                    "content": document
                })
                
            return formatted_results
            
        except Exception as e:
            logger.error(f"[VectorStore] Query failed for text '{query_text[:30]}...': {str(e)}")
            return []

# Singleton instance for easy import across the app
memory_manager = VectorMemoryManager()
