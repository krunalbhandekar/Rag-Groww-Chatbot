import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.phases.phase4.retriever import ChromaRetriever

def main():
    base_dir = Path(__file__).parent.parent
    persist_directory = base_dir / "data" / "index" / "chroma_db"

    if not persist_directory.exists():
        print(f"Error: ChromaDB index not found at {persist_directory}")
        print("Please run scripts/phase3_embed.py first.")
        sys.exit(1)

    print("=== Phase 4: Retrieval Layer ===")
    
    retriever = ChromaRetriever(persist_directory=str(persist_directory))
    
    test_queries = [
        {"query": "What is the exit load?", "scheme_id": "hdfc_elss_tax_saver_direct_plan_growth"},
        {"query": "Minimum SIP amount", "scheme_id": None},
        {"query": "What is the expense ratio?", "scheme_id": "hdfc_mid_cap_direct_growth"} # Assuming this scheme exists or will return empty if not
    ]
    
    for tq in test_queries:
        print(f"\nQuery: '{tq['query']}'")
        print(f"Scheme Hint: {tq['scheme_id']}")
        
        chunks = retriever.retrieve(query=tq['query'], scheme_id_hint=tq['scheme_id'], top_k=2)
        
        if not chunks:
            print("No chunks retrieved.")
        else:
            for i, chunk in enumerate(chunks):
                print(f"  Result {i+1} (distance: {chunk['distance']:.4f})")
                print(f"  Source: {chunk['metadata'].get('source_url')}")
                text_preview = chunk['text'][:150].replace('\n', ' ') + "..."
                print(f"  Text: {text_preview}")

if __name__ == "__main__":
    main()
