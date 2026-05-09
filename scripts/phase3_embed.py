import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.phases.phase3.index_builder import ChromaIndexBuilder

def main():
    base_dir = Path(__file__).parent.parent
    chunks_file = base_dir / "data" / "chunks" / "chunks.jsonl"
    persist_directory = base_dir / "data" / "index" / "chroma_db"
    version_file = base_dir / "data" / "index" / "version.json"

    if not chunks_file.exists():
        print(f"Error: Chunks file not found at {chunks_file}")
        print("Please run phase 2 first.")
        sys.exit(1)

    print("=== Phase 3: Building Vector Index ===")
    
    # We use sentence-transformers all-MiniLM-L6-v2 by default
    builder = ChromaIndexBuilder(
        persist_directory=str(persist_directory),
        embedding_model_name='all-MiniLM-L6-v2',
        collection_name='groww_schemes'
    )
    
    version_data = builder.build_index(
        chunks_file_path=str(chunks_file),
        version_file_path=str(version_file)
    )
    
    if version_data:
        print("\nVerification:")
        print(f"Total documents indexed: {version_data.get('document_count')}")
        print(f"Index build ID: {version_data.get('index_build_id')}")
        print("Done.")

if __name__ == "__main__":
    main()
