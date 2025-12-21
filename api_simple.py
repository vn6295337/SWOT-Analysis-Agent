#!/usr/bin/env python3
"""
Simplified API for A2A Strategy Agent
This version is designed to work reliably in Hugging Face Spaces
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import json
import traceback

# Initialize FastAPI app
app = FastAPI(title="A2A Strategy Agent - Simple API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class AnalysisRequest(BaseModel):
    company_name: str

class AnalysisResponse(BaseModel):
    company_name: str
    draft_report: Optional[str] = None
    critique: Optional[str] = None
    score: Optional[float] = None
    revision_count: int = 0
    report_length: int = 0
    status: str = "completed"
    current_step: str = "completed"
    progress: float = 100.0
    error: Optional[str] = None

# Sample SWOT data for demo purposes
def generate_sample_swot(company_name: str) -> str:
    """Generate a sample SWOT analysis"""
    return f"""# SWOT Analysis for {company_name}

## Strengths
- Strong brand recognition in the {company_name.lower()} industry
- Innovative products and cutting-edge technology
- Experienced leadership and management team
- Global market presence and distribution network
- Strong financial performance and market position

## Weaknesses
- Dependence on key personnel and leadership
- High production and operational costs
- Limited product diversity compared to competitors
- Supply chain vulnerabilities and dependencies
- Regulatory and compliance challenges

## Opportunities
- Expansion into emerging international markets
- Strategic partnerships with technology companies
- Growing demand for sustainable and eco-friendly products
- Government incentives and grants for innovation
- Increasing consumer demand for premium products

## Threats
- Intensifying competition from established players
- Economic downturns and market volatility
- Rapid technological changes and disruption
- Changing regulatory landscape and compliance requirements
- Supply chain disruptions and geopolitical risks

## Strategic Recommendations

Based on this SWOT analysis, {company_name} should focus on:

1. **Leveraging Strengths**: Continue investing in innovation and technology leadership while expanding global market presence.

2. **Addressing Weaknesses**: Diversify product portfolio to reduce dependence on key products and strengthen supply chain resilience.

3. **Capitalizing on Opportunities**: Accelerate expansion into emerging markets and form strategic partnerships to drive growth.

4. **Mitigating Threats**: Monitor competitive landscape closely and develop contingency plans for economic and regulatory challenges.

## Quality Score: 8.5/10

This analysis provides comprehensive coverage of {company_name}'s strategic position with actionable recommendations.
"""

def generate_sample_critique() -> str:
    """Generate a sample critique"""
    return "The analysis provides comprehensive coverage of the company's strategic position with clear strengths, weaknesses, opportunities, and threats. Recommendations are actionable and well-supported by the analysis. Overall quality meets professional standards for strategic business analysis."

# API Endpoints
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "A2A Strategy Agent API is running",
        "version": "1.0.0"
    }

@app.post("/api/analyze", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest):
    """Start a new analysis workflow"""
    try:
        # Generate sample SWOT data
        draft_report = generate_sample_swot(request.company_name)
        critique = generate_sample_critique()
        score = 8.5
        
        return AnalysisResponse(
            company_name=request.company_name,
            draft_report=draft_report,
            critique=critique,
            score=score,
            revision_count=1,
            report_length=len(draft_report),
            status="completed",
            current_step="completed",
            progress=100.0
        )
        
    except Exception as e:
        error_msg = f"Analysis failed: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/api/status/{workflow_id}", response_model=AnalysisResponse)
async def get_status(workflow_id: str):
    """Get the current status of a workflow"""
    # For demo purposes, return completed status
    company_name = workflow_id.replace('_workflow', '').replace('_', ' ').title()
    
    return AnalysisResponse(
        company_name=company_name,
        draft_report=generate_sample_swot(company_name),
        critique=generate_sample_critique(),
        score=8.5,
        revision_count=1,
        report_length=2500,
        status="completed",
        current_step="completed",
        progress=100.0
    )

@app.post("/api/process/{workflow_id}", response_model=AnalysisResponse)
async def process_workflow(workflow_id: str):
    """Process the workflow step by step"""
    # For demo purposes, return completed status immediately
    company_name = workflow_id.replace('_workflow', '').replace('_', ' ').title()
    
    return AnalysisResponse(
        company_name=company_name,
        draft_report=generate_sample_swot(company_name),
        critique=generate_sample_critique(),
        score=8.5,
        revision_count=1,
        report_length=2500,
        status="completed",
        current_step="completed",
        progress=100.0
    )

@app.get("/api/swot/{workflow_id}")
async def get_swot_data(workflow_id: str):
    """Get structured SWOT data"""
    company_name = workflow_id.replace('_workflow', '').replace('_', ' ').title()
    draft_report = generate_sample_swot(company_name)
    
    # Parse SWOT data
    swot_data = {
        "strengths": [
            "Strong brand recognition in the industry",
            "Innovative products and cutting-edge technology",
            "Experienced leadership and management team",
            "Global market presence and distribution network",
            "Strong financial performance and market position"
        ],
        "weaknesses": [
            "Dependence on key personnel and leadership",
            "High production and operational costs",
            "Limited product diversity compared to competitors",
            "Supply chain vulnerabilities and dependencies",
            "Regulatory and compliance challenges"
        ],
        "opportunities": [
            "Expansion into emerging international markets",
            "Strategic partnerships with technology companies",
            "Growing demand for sustainable and eco-friendly products",
            "Government incentives and grants for innovation",
            "Increasing consumer demand for premium products"
        ],
        "threats": [
            "Intensifying competition from established players",
            "Economic downturns and market volatility",
            "Rapid technological changes and disruption",
            "Changing regulatory landscape and compliance requirements",
            "Supply chain disruptions and geopolitical risks"
        ]
    }
    
    return swot_data

if __name__ == "__main__":
    import uvicorn
    import os
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8002))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting A2A Strategy Agent API on {host}:{port}")
    print("📋 This is a simplified version that works without external API calls")
    print("💡 For full functionality, ensure you have:")
    print("   - GROQ_API_KEY")
    print("   - TAVILY_API_KEY")
    print("   - LANGCHAIN_API_KEY")
    
    uvicorn.run(app, host=host, port=port)