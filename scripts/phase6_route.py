import sys
import os

# Add src to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.phases.phase6.router import QueryRouter

def main():
    print("=== Phase 6: Refusal Routing and Performance Queries ===")
    
    router = QueryRouter()
    
    test_queries = [
        "What is the expense ratio of this fund?",
        "Should I buy this fund?",
        "What is the 1Y return for HDFC Mid Cap?",
        "Which is better, HDFC or SBI?",
        "Here is my PAN card for KYC.",
        "What is the exit load?"
    ]
    
    for q in test_queries:
        print(f"\nQ: '{q}'")
        result = router.route_query(q)
        
        print(f"Route: {result['route'].upper()}")
        print(f"Proceed to RAG: {result['proceed_to_rag']}")
        
        if not result['proceed_to_rag']:
            print(f"Response: {result['response']}")

if __name__ == "__main__":
    main()
