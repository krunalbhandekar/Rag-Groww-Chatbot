import json
import os
import hashlib
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

class ChromaIndexBuilder:
    def __init__(self, persist_directory: str, embedding_model_name: str = 'all-MiniLM-L6-v2', collection_name: str = 'groww_schemes'):
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model_name
        self.collection_name = collection_name
        
        # Ensure persistence directory exists
        os.makedirs(self.persist_directory, exist_ok=True)
        
        print(f"Loading embedding model: {self.embedding_model_name}")
        self.model = SentenceTransformer(self.embedding_model_name)
        
        print(f"Initializing ChromaDB client at: {self.persist_directory}")
        self.client = chromadb.PersistentClient(path=self.persist_directory)
        
        # We recreate the collection to ensure a fresh index per build
        try:
            self.client.delete_collection(name=self.collection_name)
        except Exception:
            pass # Collection might not exist yet
            
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        # sentence-transformers outputs a list of numpy arrays, we convert to lists
        embeddings = self.model.encode(texts, convert_to_numpy=True).tolist()
        return embeddings

    def build_index(self, chunks_file_path: str, version_file_path: str):
        print(f"Reading chunks from {chunks_file_path}")
        chunks = []
        with open(chunks_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    chunks.append(json.loads(line))
        
        if not chunks:
            print("No chunks found.")
            return

        print(f"Found {len(chunks)} chunks. Generating embeddings...")
        
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.generate_embeddings(texts)
        
        ids = []
        metadatas = []
        documents = []
        
        # We need a stable hash for the entire corpus to store in version.json
        corpus_manifest_hash_obj = hashlib.md5()
        
        for i, chunk in enumerate(chunks):
            chunk_metadata = chunk.get('metadata', {})
            # ID can be a combination of snapshot_id and a hash of the text to ensure uniqueness
            text_hash = hashlib.md5(chunk['text'].encode('utf-8')).hexdigest()
            doc_id = f"{chunk_metadata.get('scheme_id', 'unknown')}_{text_hash}"
            ids.append(doc_id)
            documents.append(chunk['text'])
            
            # ChromaDB metadata values must be str, int, float or bool
            sanitized_metadata = {}
            for k, v in chunk_metadata.items():
                if v is None:
                    continue
                if isinstance(v, (str, int, float, bool)):
                    sanitized_metadata[k] = v
                else:
                    sanitized_metadata[k] = str(v)
            metadatas.append(sanitized_metadata)
            
            corpus_manifest_hash_obj.update(doc_id.encode('utf-8'))
        
        print(f"Adding {len(documents)} documents to ChromaDB collection...")
        # Add to Chroma in batches if needed, but for small dataset we can add directly
        # ChromaDB handles batching internally up to a limit.
        batch_size = 100
        for i in range(0, len(documents), batch_size):
            self.collection.add(
                ids=ids[i:i+batch_size],
                embeddings=embeddings[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
                documents=documents[i:i+batch_size]
            )
            
        corpus_manifest_hash = corpus_manifest_hash_obj.hexdigest()
        
        # Create version.json for build determinism
        import uuid
        build_id = str(uuid.uuid4())
        version_data = {
            "embedding_model": self.embedding_model_name,
            "index_build_id": build_id,
            "corpus_manifest_hash": corpus_manifest_hash,
            "document_count": len(documents)
        }
        
        os.makedirs(os.path.dirname(version_file_path), exist_ok=True)
        with open(version_file_path, 'w', encoding='utf-8') as f:
            json.dump(version_data, f, indent=2)
            
        print(f"Index built successfully! Wrote version info to {version_file_path}")
        return version_data
