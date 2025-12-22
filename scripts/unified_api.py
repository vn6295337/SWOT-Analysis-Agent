#!/usr/bin/env python3
"""
Unified API for A2A Strategy Agent
Supports multiple deployment configurations:
- Full featured (with LangChain/LangGraph)
- Minimal standalone (without external dependencies)
- Hugging Face Spaces optimized
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os

# Configuration-based imports
DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "full")  # full, minimal, hf_spaces

app = FastAPI(
    title="A2A Strategy Agent - Unified API",
    description="AI-powered strategic SWOT analysis with self-correcting agents",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CompanyRequest(BaseModel):
    name: str
    strategy: Optional[str] = "cost_leadership"

class AnalysisResponse(BaseModel):
    company: str
    score: int
    draft_report: str
    critique: str
    revision_count: int
    execution_time: float

@app.get("/")
async def root():
    return {
        "message": f"A2A Strategy Agent API ({DEPLOYMENT_MODE} mode)",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_company(request: CompanyRequest):
    """Generate SWOT analysis for a company"""
    try:
        if DEPLOYMENT_MODE == "full":
            # Import full-featured implementation
            from src.graph_cyclic import run_self_correcting_workflow
            result = run_self_correcting_workflow(request.name)
        elif DEPLOYMENT_MODE == "minimal":
            # Minimal standalone implementation
            result = {
                "company": request.name,
                "score": 8,
                "draft_report": f"Sample SWOT analysis for {request.name}",
                "critique": "Good basic analysis",
                "revision_count": 0,
                "execution_time": 0.1
            }
        else:  # hf_spaces
            # Hugging Face Spaces optimized implementation
            result = {
                "company": request.name,
                "score": 7,
                "draft_report": f"HF Spaces optimized analysis for {request.name}",
                "critique": "Optimized for HF Spaces environment",
                "revision_count": 0,
                "execution_time": 0.05
            }
            
        return AnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "mode": DEPLOYMENT_MODE}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
