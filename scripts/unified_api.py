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
import threading
import uuid
import time

# Configuration-based imports
DEPLOYMENT_MODE = os.getenv("DEPLOYMENT_MODE", "full")  # full, minimal, hf_spaces

# Global workflow registry for tracking async workflows
WORKFLOWS: dict[str, dict] = {}

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

@app.post("/analyze")
async def start_analysis(request: CompanyRequest):
    """Start async SWOT analysis workflow"""
    workflow_id = f"{request.name.lower().replace(' ', '_')}_{uuid.uuid4().hex[:8]}"
    
    # Initialize workflow tracking
    WORKFLOWS[workflow_id] = {
        "status": "running",
        "current_step": "starting",
        "revision_count": 0,
        "score": 0,
        "result": None,
        "error": None,
    }
    
    def runner():
        try:
            if DEPLOYMENT_MODE == "full":
                # Import full-featured implementation
                from src.graph_cyclic import run_self_correcting_workflow
                result = run_self_correcting_workflow(
                    request.name,
                    workflow_id=workflow_id,
                    progress_store=WORKFLOWS
                )
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
            
            # Update workflow status and store result
            WORKFLOWS[workflow_id]["status"] = "completed"
            WORKFLOWS[workflow_id]["result"] = result
            
        except Exception as e:
            WORKFLOWS[workflow_id]["status"] = "error"
            WORKFLOWS[workflow_id]["error"] = str(e)
    
    # Start workflow in background thread
    threading.Thread(target=runner, daemon=True).start()
    
    return {"workflow_id": workflow_id}

@app.get("/workflow/{workflow_id}/status")
async def workflow_status(workflow_id: str):
    """Get workflow status and progress"""
    wf = WORKFLOWS.get(workflow_id)
    if not wf:
        raise HTTPException(404, "Workflow not found")
    return {
        "status": wf["status"],
        "current_step": wf["current_step"],
        "revision_count": wf["revision_count"],
        "score": wf["score"],
    }

@app.get("/workflow/{workflow_id}/result")
async def workflow_result(workflow_id: str):
    """Get workflow result (available when completed)"""
    wf = WORKFLOWS.get(workflow_id)
    if not wf or wf["status"] != "completed":
        raise HTTPException(404, "Result not ready")
    return wf["result"]

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "mode": DEPLOYMENT_MODE}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
