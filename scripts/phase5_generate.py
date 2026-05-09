"""
Phase 5 operator script: Run generation on a sample chunk set using Groq.

Usage:
    python3 scripts/phase5_generate.py

Requires:
    - GROQ_API_KEY set in .env or environment
    - data/chunks/chunks.jsonl produced by scripts/phase2_chunk.py
"""
import json
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.phases.phase4.retriever import ChromaRetriever
from src.phases.phase5 import GroqGenerator

DEMO_QUESTIONS = [
    {"query": "What is the minimum SIP amount?", "scheme_id": "hdfc_mid_cap_direct_growth"},
    {"query": "What is the exit load for this fund?", "scheme_id": "hdfc_elss_tax_saver_direct_plan_growth"},
    {"query": "What is the expense ratio?", "scheme_id": None},
]

def main():
    print("Phase 5 — Groq generation demo (with Phase 4 retrieval)\n" + "=" * 60)
    
    base_dir = Path(__file__).parent.parent
    persist_directory = base_dir / "data" / "index" / "chroma_db"
    
    if not persist_directory.exists():
        print(f"Error: ChromaDB index not found at {persist_directory}")
        sys.exit(1)

    try:
        retriever = ChromaRetriever(persist_directory=str(persist_directory))
        print("Initialized ChromaRetriever.")
        generator = GroqGenerator()
        print(f"Initialized GroqGenerator with model: {generator.model_name}\n")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print("-" * 60)
    
    for item in DEMO_QUESTIONS:
        question = item["query"]
        scheme_id = item["scheme_id"]
        
        print(f"Q: {question} (Hint: {scheme_id})")
        
        # Phase 4 Retrieval
        chunks = retriever.retrieve(query=question, scheme_id_hint=scheme_id, top_k=3)
        print(f"Retrieved {len(chunks)} chunks.")
        
        # Phase 5 Generation
        result = generator.generate_answer(question, chunks)
        
        print(f"\nA:\n{result.get('formatted_response', result.get('answer'))}")
        print("-" * 60)


if __name__ == "__main__":
    main()
