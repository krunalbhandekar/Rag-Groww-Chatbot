import os
import re
from typing import Dict, Any, Optional
from pathlib import Path

from src.phases.phase4.retriever import ChromaRetriever
from src.phases.phase5 import GroqGenerator
from src.phases.phase6.router import QueryRouter

class ChatOrchestrator:
    """
    Coordinates Phase 4 (Retrieval), Phase 5 (Generation), and Phase 6 (Routing).
    """
    def __init__(self, base_dir: Path):
        persist_directory = base_dir / "data" / "index" / "chroma_db"
        
        print("Initializing QueryRouter (Phase 6)...")
        self.router = QueryRouter()
        
        print("Initializing ChromaRetriever (Phase 4)...")
        self.retriever = ChromaRetriever(persist_directory=str(persist_directory))
        
        print("Initializing GroqGenerator (Phase 5)...")
        self.generator = GroqGenerator()
        self.scheme_mappings = [
            {
                "scheme_id": "hdfc_mid_cap_direct_growth",
                "source_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
                "aliases": ["hdfc mid cap", "mid cap", "hdfc midcap", "midcap"],
            },
            {
                "scheme_id": "hdfc_equity_direct_growth",
                "source_url": "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
                "aliases": ["hdfc equity", "equity fund"],
            },
            {
                "scheme_id": "hdfc_focused_direct_growth",
                "source_url": "https://groww.in/mutual-funds/hdfc-focused-fund-direct-growth",
                "aliases": ["hdfc focused", "focused fund"],
            },
            {
                "scheme_id": "hdfc_elss_tax_saver_direct_plan_growth",
                "source_url": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
                "aliases": ["hdfc elss", "tax saver", "elss"],
            },
            {
                "scheme_id": "hdfc_large_cap_direct_growth",
                "source_url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
                "aliases": ["hdfc large cap", "large cap"],
            },
        ]

    def _resolve_scheme_from_message(self, message: str) -> Dict[str, Optional[str]]:
        message_lower = message.lower()
        for mapping in self.scheme_mappings:
            for alias in mapping["aliases"]:
                if re.search(rf"\b{re.escape(alias)}\b", message_lower):
                    return {
                        "scheme_id": mapping["scheme_id"],
                        "source_url": mapping["source_url"],
                    }
        return {"scheme_id": None, "source_url": None}

    def process_message(self, message: str, scheme_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Processes a chat message through the RAG pipeline.
        Returns a dict matching Phase 7 API response format (without build_id).
        """
        # Resolve scheme from explicit hint first; otherwise infer from message text.
        detected = self._resolve_scheme_from_message(message)
        effective_scheme_id = scheme_id or detected["scheme_id"]
        effective_scheme_url = detected["source_url"]

        # Phase 6: Route Query
        route_result = self.router.route_query(message, scheme_url=effective_scheme_url)
        
        if not route_result["proceed_to_rag"]:
            # It's an advisory, comparison, or OOD query
            return {
                "answer": route_result["response"],
                "citation_url": route_result["citation_url"],
                "route": route_result["route"]
            }
            
        # Phase 4: Retrieval
        chunks = self.retriever.retrieve(query=message, scheme_id_hint=effective_scheme_id, top_k=3)
        
        # Phase 5: Generation
        gen_result = self.generator.generate_answer(message, chunks)
        
        return {
            "answer": gen_result.get("formatted_response", gen_result.get("answer")),
            "citation_url": gen_result.get("citation_url"),
            "route": "factual"
        }
