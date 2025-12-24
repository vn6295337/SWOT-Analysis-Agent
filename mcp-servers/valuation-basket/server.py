"""
Valuation Basket MCP Server

Stock valuation multiples from Yahoo Finance.
Provides valuation context for SWOT analysis:
- P/E Ratio → Price relative to earnings
- P/S Ratio → Price relative to sales
- P/B Ratio → Price relative to book value
- EV/EBITDA → Enterprise value multiple
- PEG Ratio → P/E adjusted for growth

Usage:
    python server.py

Or via MCP:
    Add to claude_desktop_config.json
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

# Load environment variables
from dotenv import load_dotenv
env_paths = [
    Path.home() / ".env",
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent.parent / ".env",
]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break

# MCP SDK
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Data fetching
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("valuation-basket")

# Initialize MCP server
server = Server("valuation-basket")

# Yahoo Finance headers
YAHOO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}


# ============================================================
# DATA FETCHERS
# ============================================================

async def fetch_yahoo_quote(ticker: str) -> Optional[dict]:
    """
    Fetch quote summary from Yahoo Finance.
    Returns valuation metrics including P/E, P/S, P/B, EV/EBITDA, PEG.
    """
    try:
        async with httpx.AsyncClient() as client:
            # Use quoteSummary endpoint for detailed metrics
            url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
            params = {
                "modules": "summaryDetail,defaultKeyStatistics,financialData"
            }

            response = await client.get(url, params=params, headers=YAHOO_HEADERS, timeout=15)

            if response.status_code != 200:
                return {"error": f"Yahoo API returned {response.status_code}"}

            data = response.json()

            if "quoteSummary" not in data or not data["quoteSummary"]["result"]:
                return {"error": "No data found for ticker"}

            result = data["quoteSummary"]["result"][0]

            summary = result.get("summaryDetail", {})
            key_stats = result.get("defaultKeyStatistics", {})
            financial = result.get("financialData", {})

            return {
                "ticker": ticker.upper(),
                "summary_detail": summary,
                "key_statistics": key_stats,
                "financial_data": financial,
                "source": "Yahoo Finance"
            }

    except Exception as e:
        logger.error(f"Yahoo quote fetch error for {ticker}: {e}")
        return {"error": str(e)}


def safe_get(data: dict, key: str) -> Optional[float]:
    """Safely extract numeric value from Yahoo Finance response."""
    value = data.get(key, {})
    if isinstance(value, dict):
        return value.get("raw")
    return value if isinstance(value, (int, float)) else None


async def fetch_pe_ratio(ticker: str) -> dict:
    """
    Fetch P/E ratio (Price to Earnings).
    Lower P/E may indicate undervaluation or low growth expectations.
    """
    data = await fetch_yahoo_quote(ticker)

    if "error" in data:
        return {"metric": "P/E Ratio", "ticker": ticker, **data}

    summary = data.get("summary_detail", {})
    key_stats = data.get("key_statistics", {})

    trailing_pe = safe_get(summary, "trailingPE")
    forward_pe = safe_get(summary, "forwardPE") or safe_get(key_stats, "forwardPE")

    # Use trailing P/E as primary, forward P/E as secondary
    pe_value = trailing_pe or forward_pe

    if pe_value is None:
        return {
            "metric": "P/E Ratio",
            "ticker": ticker.upper(),
            "error": "P/E data not available (company may have negative earnings)"
        }

    # P/E interpretation (varies by sector, these are general guidelines)
    if pe_value < 0:
        interpretation = "Negative P/E - Company has losses"
        swot_impact = "WEAKNESS"
    elif pe_value < 10:
        interpretation = "Low P/E - May be undervalued or facing challenges"
        swot_impact = "OPPORTUNITY"
    elif pe_value < 20:
        interpretation = "Moderate P/E - Fair valuation"
        swot_impact = "NEUTRAL"
    elif pe_value < 30:
        interpretation = "High P/E - Growth expectations priced in"
        swot_impact = "NEUTRAL"
    elif pe_value < 50:
        interpretation = "Very high P/E - High growth expectations"
        swot_impact = "WEAKNESS"
    else:
        interpretation = "Extremely high P/E - Speculative valuation"
        swot_impact = "WEAKNESS"

    return {
        "metric": "P/E Ratio",
        "ticker": ticker.upper(),
        "trailing_pe": round(trailing_pe, 2) if trailing_pe else None,
        "forward_pe": round(forward_pe, 2) if forward_pe else None,
        "value": round(pe_value, 2),
        "interpretation": interpretation,
        "swot_category": swot_impact,
        "source": data["source"],
        "as_of": datetime.now().isoformat()
    }


async def fetch_ps_ratio(ticker: str) -> dict:
    """
    Fetch P/S ratio (Price to Sales).
    Useful for companies with negative earnings.
    """
    data = await fetch_yahoo_quote(ticker)

    if "error" in data:
        return {"metric": "P/S Ratio", "ticker": ticker, **data}

    summary = data.get("summary_detail", {})
    key_stats = data.get("key_statistics", {})

    ps_ratio = safe_get(summary, "priceToSalesTrailing12Months") or safe_get(key_stats, "priceToSalesTrailing12Months")

    if ps_ratio is None:
        return {
            "metric": "P/S Ratio",
            "ticker": ticker.upper(),
            "error": "P/S data not available"
        }

    # P/S interpretation
    if ps_ratio < 1:
        interpretation = "Low P/S - Trading below 1x sales, potentially undervalued"
        swot_impact = "OPPORTUNITY"
    elif ps_ratio < 3:
        interpretation = "Moderate P/S - Reasonable valuation relative to revenue"
        swot_impact = "NEUTRAL"
    elif ps_ratio < 8:
        interpretation = "High P/S - Premium valuation, high growth expected"
        swot_impact = "NEUTRAL"
    elif ps_ratio < 15:
        interpretation = "Very high P/S - Aggressive growth assumptions"
        swot_impact = "WEAKNESS"
    else:
        interpretation = "Extremely high P/S - Speculative valuation"
        swot_impact = "WEAKNESS"

    return {
        "metric": "P/S Ratio",
        "ticker": ticker.upper(),
        "value": round(ps_ratio, 2),
        "interpretation": interpretation,
        "swot_category": swot_impact,
        "source": data["source"],
        "as_of": datetime.now().isoformat()
    }


async def fetch_pb_ratio(ticker: str) -> dict:
    """
    Fetch P/B ratio (Price to Book).
    Compares market value to book value.
    """
    data = await fetch_yahoo_quote(ticker)

    if "error" in data:
        return {"metric": "P/B Ratio", "ticker": ticker, **data}

    key_stats = data.get("key_statistics", {})

    pb_ratio = safe_get(key_stats, "priceToBook")

    if pb_ratio is None:
        return {
            "metric": "P/B Ratio",
            "ticker": ticker.upper(),
            "error": "P/B data not available"
        }

    # P/B interpretation
    if pb_ratio < 1:
        interpretation = "Below book value - May be undervalued or have asset issues"
        swot_impact = "OPPORTUNITY"
    elif pb_ratio < 3:
        interpretation = "Moderate P/B - Trading near tangible asset value"
        swot_impact = "NEUTRAL"
    elif pb_ratio < 5:
        interpretation = "High P/B - Intangible assets or growth premium"
        swot_impact = "NEUTRAL"
    else:
        interpretation = "Very high P/B - Significant intangible value priced in"
        swot_impact = "WEAKNESS"

    return {
        "metric": "P/B Ratio",
        "ticker": ticker.upper(),
        "value": round(pb_ratio, 2),
        "interpretation": interpretation,
        "swot_category": swot_impact,
        "source": data["source"],
        "as_of": datetime.now().isoformat()
    }


async def fetch_ev_ebitda(ticker: str) -> dict:
    """
    Fetch EV/EBITDA (Enterprise Value to EBITDA).
    Useful for comparing companies with different capital structures.
    """
    data = await fetch_yahoo_quote(ticker)

    if "error" in data:
        return {"metric": "EV/EBITDA", "ticker": ticker, **data}

    key_stats = data.get("key_statistics", {})

    ev_ebitda = safe_get(key_stats, "enterpriseToEbitda")

    if ev_ebitda is None:
        return {
            "metric": "EV/EBITDA",
            "ticker": ticker.upper(),
            "error": "EV/EBITDA data not available"
        }

    # Also get enterprise value for context
    ev = safe_get(key_stats, "enterpriseValue")

    # EV/EBITDA interpretation
    if ev_ebitda < 0:
        interpretation = "Negative EV/EBITDA - Negative EBITDA or unusual capital structure"
        swot_impact = "WEAKNESS"
    elif ev_ebitda < 8:
        interpretation = "Low EV/EBITDA - Potentially undervalued"
        swot_impact = "OPPORTUNITY"
    elif ev_ebitda < 12:
        interpretation = "Moderate EV/EBITDA - Fair valuation"
        swot_impact = "NEUTRAL"
    elif ev_ebitda < 20:
        interpretation = "High EV/EBITDA - Premium valuation"
        swot_impact = "NEUTRAL"
    else:
        interpretation = "Very high EV/EBITDA - Expensive relative to cash earnings"
        swot_impact = "WEAKNESS"

    return {
        "metric": "EV/EBITDA",
        "ticker": ticker.upper(),
        "value": round(ev_ebitda, 2),
        "enterprise_value": ev,
        "interpretation": interpretation,
        "swot_category": swot_impact,
        "source": data["source"],
        "as_of": datetime.now().isoformat()
    }


async def fetch_peg_ratio(ticker: str) -> dict:
    """
    Fetch PEG ratio (P/E to Growth).
    Adjusts P/E for expected growth rate.
    """
    data = await fetch_yahoo_quote(ticker)

    if "error" in data:
        return {"metric": "PEG Ratio", "ticker": ticker, **data}

    key_stats = data.get("key_statistics", {})

    peg_ratio = safe_get(key_stats, "pegRatio")

    if peg_ratio is None:
        return {
            "metric": "PEG Ratio",
            "ticker": ticker.upper(),
            "error": "PEG data not available (requires positive earnings and growth)"
        }

    # PEG interpretation
    if peg_ratio < 0:
        interpretation = "Negative PEG - Negative earnings or declining growth"
        swot_impact = "WEAKNESS"
    elif peg_ratio < 1:
        interpretation = "Low PEG (<1) - May be undervalued relative to growth"
        swot_impact = "OPPORTUNITY"
    elif peg_ratio < 1.5:
        interpretation = "Moderate PEG - Fair value relative to growth"
        swot_impact = "NEUTRAL"
    elif peg_ratio < 2:
        interpretation = "High PEG - Premium to growth rate"
        swot_impact = "NEUTRAL"
    else:
        interpretation = "Very high PEG - Overvalued relative to growth"
        swot_impact = "WEAKNESS"

    return {
        "metric": "PEG Ratio",
        "ticker": ticker.upper(),
        "value": round(peg_ratio, 2),
        "interpretation": interpretation,
        "note": "PEG < 1 often considered undervalued",
        "swot_category": swot_impact,
        "source": data["source"],
        "as_of": datetime.now().isoformat()
    }


async def get_full_valuation_basket(ticker: str) -> dict:
    """
    Fetch all valuation metrics for a given ticker.
    Returns aggregated SWOT-ready data.
    """
    # Fetch data once (to avoid multiple API calls)
    data = await fetch_yahoo_quote(ticker)

    if "error" in data:
        return {
            "ticker": ticker.upper(),
            "error": data["error"]
        }

    summary = data.get("summary_detail", {})
    key_stats = data.get("key_statistics", {})

    # Extract all metrics
    metrics = {
        "pe_ratio": {
            "trailing": safe_get(summary, "trailingPE"),
            "forward": safe_get(summary, "forwardPE") or safe_get(key_stats, "forwardPE")
        },
        "ps_ratio": safe_get(summary, "priceToSalesTrailing12Months") or safe_get(key_stats, "priceToSalesTrailing12Months"),
        "pb_ratio": safe_get(key_stats, "priceToBook"),
        "ev_ebitda": safe_get(key_stats, "enterpriseToEbitda"),
        "peg_ratio": safe_get(key_stats, "pegRatio"),
        "enterprise_value": safe_get(key_stats, "enterpriseValue"),
        "market_cap": safe_get(summary, "marketCap")
    }

    # Build SWOT summary
    swot_summary = {
        "strengths": [],
        "weaknesses": [],
        "opportunities": [],
        "threats": []
    }

    # Analyze P/E
    trailing_pe = metrics["pe_ratio"]["trailing"]
    if trailing_pe:
        if 0 < trailing_pe < 15:
            swot_summary["opportunities"].append(f"Low P/E ({trailing_pe:.1f}) - Potentially undervalued")
        elif trailing_pe > 40:
            swot_summary["weaknesses"].append(f"High P/E ({trailing_pe:.1f}) - Expensive valuation")

    # Analyze P/S
    ps = metrics["ps_ratio"]
    if ps:
        if ps < 1:
            swot_summary["opportunities"].append(f"Low P/S ({ps:.1f}) - Trading below 1x sales")
        elif ps > 10:
            swot_summary["weaknesses"].append(f"High P/S ({ps:.1f}) - Premium to revenue")

    # Analyze P/B
    pb = metrics["pb_ratio"]
    if pb:
        if pb < 1:
            swot_summary["opportunities"].append(f"Below book value (P/B {pb:.1f})")
        elif pb > 8:
            swot_summary["weaknesses"].append(f"High P/B ({pb:.1f}) - Premium to assets")

    # Analyze EV/EBITDA
    ev_ebitda = metrics["ev_ebitda"]
    if ev_ebitda:
        if 0 < ev_ebitda < 8:
            swot_summary["opportunities"].append(f"Low EV/EBITDA ({ev_ebitda:.1f})")
        elif ev_ebitda > 20:
            swot_summary["weaknesses"].append(f"High EV/EBITDA ({ev_ebitda:.1f})")

    # Analyze PEG
    peg = metrics["peg_ratio"]
    if peg:
        if 0 < peg < 1:
            swot_summary["opportunities"].append(f"Low PEG ({peg:.2f}) - Undervalued vs growth")
        elif peg > 2:
            swot_summary["weaknesses"].append(f"High PEG ({peg:.2f}) - Overvalued vs growth")

    # Overall assessment
    opp_count = len(swot_summary["opportunities"])
    weak_count = len(swot_summary["weaknesses"])

    if opp_count >= 3:
        overall = "Potentially undervalued on multiple metrics"
    elif weak_count >= 3:
        overall = "Premium valuation on multiple metrics"
    elif opp_count > weak_count:
        overall = "Relatively attractive valuation"
    elif weak_count > opp_count:
        overall = "Relatively expensive valuation"
    else:
        overall = "Mixed valuation signals"

    # Round metrics for output
    formatted_metrics = {
        "pe_ratio": {
            "trailing": round(trailing_pe, 2) if trailing_pe else None,
            "forward": round(metrics["pe_ratio"]["forward"], 2) if metrics["pe_ratio"]["forward"] else None
        },
        "ps_ratio": round(ps, 2) if ps else None,
        "pb_ratio": round(pb, 2) if pb else None,
        "ev_ebitda": round(ev_ebitda, 2) if ev_ebitda else None,
        "peg_ratio": round(peg, 2) if peg else None,
        "enterprise_value": metrics["enterprise_value"],
        "market_cap": metrics["market_cap"]
    }

    return {
        "ticker": ticker.upper(),
        "metrics": formatted_metrics,
        "overall_assessment": overall,
        "swot_summary": swot_summary,
        "source": "Yahoo Finance",
        "generated_at": datetime.now().isoformat()
    }


# ============================================================
# MCP TOOL DEFINITIONS
# ============================================================

@server.list_tools()
async def list_tools():
    """List available valuation tools."""
    return [
        Tool(
            name="get_pe_ratio",
            description="Get P/E ratio (Price to Earnings) for a stock. Compares price to earnings per share.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol (e.g., AAPL, TSLA)"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_ps_ratio",
            description="Get P/S ratio (Price to Sales) for a stock. Useful for companies with negative earnings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_pb_ratio",
            description="Get P/B ratio (Price to Book) for a stock. Compares market value to book value.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_ev_ebitda",
            description="Get EV/EBITDA for a stock. Enterprise value relative to operating earnings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_peg_ratio",
            description="Get PEG ratio for a stock. P/E adjusted for expected growth rate.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["ticker"]
            }
        ),
        Tool(
            name="get_valuation_basket",
            description="Get full valuation basket (P/E, P/S, P/B, EV/EBITDA, PEG) with aggregated SWOT summary.",
            inputSchema={
                "type": "object",
                "properties": {
                    "ticker": {
                        "type": "string",
                        "description": "Stock ticker symbol"
                    }
                },
                "required": ["ticker"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool invocations."""
    try:
        ticker = arguments.get("ticker", "").upper()
        if not ticker and name != "get_macro_basket":
            return [TextContent(type="text", text="Error: ticker is required")]

        if name == "get_pe_ratio":
            result = await fetch_pe_ratio(ticker)
        elif name == "get_ps_ratio":
            result = await fetch_ps_ratio(ticker)
        elif name == "get_pb_ratio":
            result = await fetch_pb_ratio(ticker)
        elif name == "get_ev_ebitda":
            result = await fetch_ev_ebitda(ticker)
        elif name == "get_peg_ratio":
            result = await fetch_peg_ratio(ticker)
        elif name == "get_valuation_basket":
            result = await get_full_valuation_basket(ticker)
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        logger.error(f"Tool error {name}: {e}")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


# ============================================================
# MAIN
# ============================================================

async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
