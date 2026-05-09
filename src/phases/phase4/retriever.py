import os
from typing import List, Dict, Optional
import chromadb
from sentence_transformers import SentenceTransformer

class ChromaRetriever:
    """
    Phase 4: Retriever
    Retrieves small, precise evidence given a factual query and optional scheme hint.
    """
    def __init__(self, persist_directory: str, embedding_model_name: str = 'all-MiniLM-L6-v2', collection_name: str = 'groww_schemes'):
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model_name
        self.collection_name = collection_name
        
        # Load the same embedding model used in Phase 3
        self.model = SentenceTransformer(self.embedding_model_name)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
        except Exception as e:
            raise ValueError(f"Collection '{self.collection_name}' not found. Please run Phase 3 index builder first.") from e

    def retrieve(self, query: str, scheme_id_hint: Optional[str] = None, top_k: int = 3) -> List[Dict]:
        """
        Retrieves the top_k chunks for a given query.
        If scheme_id_hint is provided, physically restricts search to that scheme_id.
        Drops retrieved chunks whose source_url is absent or not allowlisted.
        """
        query_embedding = self.model.encode(query, convert_to_numpy=True).tolist()
        
        where_filter = None
        if scheme_id_hint:
            where_filter = {"scheme_id": scheme_id_hint}
            
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k * 2, # Fetch more to account for dropped chunks
            where=where_filter,
            include=['documents', 'metadatas', 'distances']
        )
        
        if not results['documents'] or not results['documents'][0]:
            return []
            
        chunks = []
        allowlisted_urls = {
            "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
            "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
            "https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth",
            "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
            "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth"
        }
        
        for i, doc in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i]
            source_url = metadata.get('source_url')
            
            # Grounding rule: Drop retrieved chunks whose source_url is absent or not allowlisted
            if not source_url or source_url not in allowlisted_urls:
                continue
                
            chunks.append({
                "text": doc,
                "metadata": metadata,
                "distance": results['distances'][0][i]
            })
            
            if len(chunks) == top_k:
                break
                
        return chunks
