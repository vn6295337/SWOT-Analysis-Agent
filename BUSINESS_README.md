# A2A Strategy Agent

An **AI-powered strategic analysis system** that generates SWOT analyses for companies using a self-correcting workflow.

## Workflow Pipeline

```
Researcher → Analyst → Critic → Editor (loop)
```

### 4 Node Types

1. **Researcher** - Gathers real-time data via Tavily API, summarizes with LLM
2. **Analyst** - Generates SWOT analysis focused on Cost Leadership strategy
3. **Critic** - Evaluates quality (1-10 score) using a rubric
4. **Editor** - Revises based on critique if score < 7 (max 3 iterations)

## Key Technical Components

- **LangGraph** for workflow orchestration (linear & cyclic graphs)
- **Tavily API** for real-time web search
- **Groq LLM** (llama-3.1-8b-instant) for analysis
- **SQLite** database storing strategy context (Cost Leadership)
- **MCP Server** exposing database as a tool
- **LangSmith** for tracing/observability
- **Streamlit** frontend for user interface
- **FastAPI** backend (`api/`) for async workflow execution

## Quality Control System

- Rubric-based evaluation: Completeness, Specificity, Relevance, Depth (25% each)
- Self-correcting loop exits when score ≥ 7 or after 3 revisions
- Real-time progress tracking via polling (700ms intervals)

---

# Data Sources for SWOT Analysis

## Why MCP Servers?

MCP servers act as a **standardized interface** between AI agents and data sources.

| Without MCP | With MCP |
|-------------|----------|
| Each agent writes its own API code | One server, many agents can use it |
| API keys scattered in agent code | Keys managed in one place |
| Different output formats per source | Consistent JSON output |
| Agent needs to know API details | Agent just calls `get_financials("AAPL")` |
| Hard to swap data sources | Swap server, agents unchanged |

### How It Works

```
Without MCP:  Agent → [knows SEC API] → SEC
              Agent → [knows Yahoo API] → Yahoo
              Agent → [knows Tavily API] → Tavily

With MCP:     Agent → [calls tool] → MCP Server → API

              Agent doesn't care what's behind the server
```

---

## Available Data Sources

### Financials Basket (SEC EDGAR)

Official financial data from SEC filings. No API key required.

| #   | Metric               | Purpose                               | Primary Source              | Secondary Source |
| --- | -------------------- | ------------------------------------- | --------------------------- | ---------------- |
| 1   | Revenue              | Company's total sales                 | SEC EDGAR XBRL              | -                |
| 2   | Net Income           | Profit after all expenses             | SEC EDGAR XBRL              | -                |
| 3   | Gross Margin         | Pricing power indicator               | SEC EDGAR XBRL              | -                |
| 4   | Operating Margin     | Operational efficiency                | SEC EDGAR XBRL              | -                |
| 5   | Net Margin           | Overall profitability                 | SEC EDGAR XBRL              | -                |
| 6   | Revenue Growth (3yr) | Business momentum                     | SEC EDGAR XBRL              | -                |
| 7   | Total Assets         | Company size/resources                | SEC EDGAR XBRL              | -                |
| 8   | Total Liabilities    | Obligations owed                      | SEC EDGAR XBRL              | -                |
| 9   | Stockholders Equity  | Net worth                             | SEC EDGAR XBRL              | -                |
| 10  | Long-term Debt       | Future obligations                    | SEC EDGAR XBRL              | -                |
| 11  | Short-term Debt      | Near-term obligations                 | SEC EDGAR XBRL              | -                |
| 12  | Debt-to-Equity       | Leverage/risk level                   | SEC EDGAR XBRL              | -                |
| 13  | Operating Cash Flow  | Cash from operations                  | SEC EDGAR XBRL              | -                |
| 14  | Capital Expenditure  | Investment in growth                  | SEC EDGAR XBRL              | -                |
| 15  | Free Cash Flow       | Cash after investments                | SEC EDGAR XBRL              | -                |
| 16  | R&D Expense          | Innovation investment                 | SEC EDGAR XBRL              | -                |
| 17  | 8-K Material Events  | Bankruptcy, impairments, exec changes | SEC EDGAR Filings           | -                |
| 18  | Ownership Changes    | 5%+ ownership, insider trades         | SEC EDGAR (13D/13G, Form 4) | -                |
| 19  | Going Concern        | Financial distress warnings           | SEC EDGAR 10-K text         | -                |

### Volatility Basket (Market Risk)

Market risk and volatility metrics. Requires FRED API key.

| # | Metric | Purpose | Primary Source | Secondary Source |
|---|--------|---------|----------------|------------------|
| 20 | VIX Index | Market-wide fear gauge | FRED | Yahoo Finance |
| 21 | Beta | Stock volatility vs market | Yahoo Finance (calculated) | - |
| 22 | Historical Volatility | Past price stability | Yahoo Finance (calculated) | - |
| 23 | Implied Volatility | Expected future movement | Alpha Vantage | - |

### Macro Basket

Economic environment indicators. Uses FRED API.

| # | Metric | Purpose | Primary Source | Secondary Source |
|---|--------|---------|----------------|------------------|
| 24 | GDP Growth | Economic expansion/contraction | FRED | - |
| 25 | Interest Rates | Cost of borrowing | FRED | - |
| 26 | CPI / Inflation | Purchasing power erosion | FRED | - |
| 27 | Unemployment | Labor market health | FRED | - |

### Valuation Basket

Stock valuation multiples. Uses Yahoo Finance + SEC EDGAR.

| # | Metric | Purpose | Primary Source | Secondary Source |
|---|--------|---------|----------------|------------------|
| 28 | P/E Ratio | Price relative to earnings | Yahoo Finance | - |
| 29 | P/S Ratio | Price relative to sales | Yahoo Finance | - |
| 30 | P/B Ratio | Price relative to book value | Yahoo Finance | - |
| 31 | EV/EBITDA | Enterprise value multiple | Yahoo + SEC | - |
| 32 | PEG Ratio | P/E adjusted for growth | Yahoo Finance | - |

### News Basket (Tavily)

Real-time news and web content. Requires Tavily API key.

| # | Metric | Purpose | Primary Source | Secondary Source |
|---|--------|---------|----------------|------------------|
| 33 | Company News | Recent coverage and sentiment | Tavily API | - |
| 34 | Going Concern News | Financial distress coverage | Tavily API | - |
| 35 | Industry Trends | Sector outlook and forecasts | Tavily API | - |
| 36 | Competitor News | Peer company coverage | Tavily API | - |

### Sentiment Basket

Market sentiment indicators from multiple free sources.

| # | Metric | Purpose | Primary Source | Secondary Source |
|---|--------|---------|----------------|------------------|
| 37 | News Sentiment | Bullish/bearish news score | Finnhub + VADER | - |
| 38 | Retail Sentiment | WallStreetBets/stocks buzz | Reddit + VADER | - |

---

## Baskets Summary

| # | Basket | Status | Metrics |
|---|--------|--------|---------|
| 1 | Financials | ✓ Done | 1-19 |
| 2 | Volatility | ✓ Done | 20-23 |
| 3 | Macro | ✓ Done | 24-27 |
| 4 | Valuation | ✓ Done | 28-32 |
| 5 | News | ✓ Done | 33-36 |
| 6 | Sentiment | ✓ Done | 37-38 |

---

## API Keys Required

| MCP Server        | API Key | Cost                | Registration                                      |
| ----------------- | ------- | ------------------- | ------------------------------------------------- |
| Financials Basket | SEC     | Free                | -                                                 |
| Volatility Basket | FRED    | Free                | https://fred.stlouisfed.org/docs/api/api_key.html |
| Macro Basket      | FRED    | Free                | https://fred.stlouisfed.org/docs/api/api_key.html |
| Valuation Basket  | None    | Free                | -                                                 |
| News Basket       | Tavily  | Free (1,000/month)  | https://tavily.com                                |
| Sentiment Basket  | Finnhub | Free (60 calls/min) | https://finnhub.io/register                       |
| Sentiment Basket  | Reddit  | Free (100 req/min)  | -                                                 |

---

## How Metrics Map to SWOT

| Category | Metrics That Indicate |
|----------|----------------------|
| **Strengths** | High margins, positive growth, strong cash flow, low debt |
| **Weaknesses** | Thin margins, high leverage, negative cash flow, exec departures |
| **Opportunities** | High R&D spend, activist investors (13D), positive news sentiment |
| **Threats** | Going concern warnings, bankruptcy filings, high VIX, delisting notices |
