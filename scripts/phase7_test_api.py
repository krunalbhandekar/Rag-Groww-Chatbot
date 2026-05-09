import requests
import time
import subprocess
import sys

def main():
    print("Starting API server in the background...")
    process = subprocess.Popen([sys.executable, "-m", "uvicorn", "src.api:app", "--port", "8000"])
    
    # Wait for server to start
    time.sleep(15)
    
    url = "http://127.0.0.p1:8000/chat"
    url = "http://127.0.0.1:8000/chat"
    
    queries = [
        {"message": "What is the exit load?", "scheme_id": "hdfc_elss_tax_saver_direct_plan_growth"},
        {"message": "Should I invest in this fund?", "scheme_id": None},
        {"message": "What is the 1Y return?", "scheme_id": "hdfc_mid_cap_direct_growth"}
    ]
    
    print("Testing /chat endpoint...\n")
    try:
        for q in queries:
            print(f"Request: {q}")
            response = requests.post(url, json=q)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.json()}\n")
            print("-" * 60)
    finally:
        print("Shutting down API server...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    main()
