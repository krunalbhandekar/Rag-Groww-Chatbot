import json
import os
from typing import Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from src.orchestrator import ChatOrchestrator

app = FastAPI(
    title="Mutual Fund RAG Chatbot API",
    description="Backend API for facts-only mutual fund FAQ assistant.",
    version="1.0.0"
)

allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]
if not allowed_origins:
    # Safe local defaults. In production set ALLOWED_ORIGINS explicitly.
    allowed_origins = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

base_dir = Path(__file__).parent.parent
frontend_dir = base_dir / "frontend"

app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
async def root():
    return FileResponse(frontend_dir / "index.html")


@app.get("/health")
async def health():
    return {"status": "ok"}

version_file = base_dir / "data" / "index" / "version.json"

try:
    with open(version_file, "r") as f:
        version_info = json.load(f)
        build_id = version_info.get("index_build_id", "unknown")
except FileNotFoundError:
    print(f"Warning: version.json not found at {version_file}. Please run phase 3 embed.")
    build_id = "unknown"

print("Initializing application components...")
try:
    orchestrator = ChatOrchestrator(base_dir=base_dir)
except Exception as e:
    print(f"Failed to initialize orchestrator: {e}")
    orchestrator = None

class ChatRequest(BaseModel):
    message: str
    scheme_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    citation_url: Optional[str]
    route: str
    build_id: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    if not orchestrator:
        raise HTTPException(status_code=500, detail="Backend components not initialized properly.")
        
    try:
        result = orchestrator.process_message(request.message, request.scheme_id)
        
        return ChatResponse(
            answer=result["answer"],
            citation_url=result["citation_url"],
            route=result["route"],
            build_id=build_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
