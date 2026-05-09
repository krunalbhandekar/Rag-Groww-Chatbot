import re
from typing import Dict, Any

class QueryRouter:
    """
    Phase 6: Query Router
    Classifies queries into Route labels: Factual, Advisory, Comparison, or OOD.
    """
    def __init__(self, default_scheme_url: str = "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth"):
        self.default_scheme_url = default_scheme_url

    def classify_intent(self, query: str) -> str:
        """
        Lightweight keyword-based classifier.
        Returns one of: 'advisory', 'comparison', 'ood', 'factual'
        """
        query_lower = query.lower()
        
        # OOD / personal
        if re.search(r'\b(pan|aadhaar|portfolio|login|account|password|otp)\b', query_lower):
            return "ood"
            
        # Advisory
        if re.search(r'\b(should i|best fund|recommend|advice|buy this)\b', query_lower):
            return "advisory"
            
        # Comparison / Returns
        if re.search(r'\b(better|compare|1y return|cagr|returns|performance)\b', query_lower):
            return "comparison"
            
        # Default to Factual
        return "factual"

    def route_query(self, query: str, scheme_url: str = None) -> Dict[str, Any]:
        """
        Routes the query and returns the action to take.
        If route is not factual, returns a formatted refusal or redirect response.
        """
        route = self.classify_intent(query)
        url_to_use = scheme_url or self.default_scheme_url
        
        if route == "ood":
            return {
                "route": route,
                "proceed_to_rag": False,
                "response": "I cannot process personal information like PAN or account details. My scope is strictly limited to factual information about mutual funds.",
                "citation_url": None
            }
            
        elif route == "advisory":
            return {
                "route": route,
                "proceed_to_rag": False,
                "response": f"I provide facts-only information and cannot offer investment advice or fund recommendations.\n\nMore details: {url_to_use}",
                "citation_url": url_to_use
            }
            
        elif route == "comparison":
            return {
                "route": route,
                "proceed_to_rag": False,
                "response": f"I do not compute or compare returns from the corpus. For performance details, please check the fund page directly.\n\nLink: {url_to_use}",
                "citation_url": url_to_use
            }
            
        # Factual
        return {
            "route": route,
            "proceed_to_rag": True,
            "response": None,
            "citation_url": None
        }
