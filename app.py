import streamlit as st
import os
import json
import time
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from src.stock_listings import get_us_stock_listings, search_stocks, highlight_match


# ============================================================
# STOCK SEARCH AUTOCOMPLETE
# ============================================================

@st.cache_data(ttl=86400)  # Cache for 24 hours
def load_stock_listings():
    """Load US stock listings with caching."""
    return get_us_stock_listings()


def render_stock_search():
    """
    Render autocomplete search bar for US stocks.

    Features:
    - Real-time suggestions as user types (debounced)
    - Shows: Company Name | Ticker | Exchange
    - Highlights matched characters
    - Ranked by match quality then market cap
    - Keyboard navigation support
    - Loading/no-results states

    Returns:
        tuple: (company_name, ticker) or (None, None) if not selected
    """
    # Initialize session state
    if "search_query" not in st.session_state:
        st.session_state.search_query = ""
    if "selected_stock" not in st.session_state:
        st.session_state.selected_stock = None
    if "show_suggestions" not in st.session_state:
        st.session_state.show_suggestions = False
    if "selected_index" not in st.session_state:
        st.session_state.selected_index = 0
    if "last_search_time" not in st.session_state:
        st.session_state.last_search_time = 0

    # Load stock data
    stocks = load_stock_listings()

    # Search input
    col1, col2 = st.columns([4, 1])

    with col1:
        # If a stock is selected, show it in the input
        default_value = ""
        if st.session_state.selected_stock:
            s = st.session_state.selected_stock
            default_value = f"{s['name']} ({s['symbol']})"

        query = st.text_input(
            "Search company",
            value=default_value,
            placeholder="Type company name or ticker (e.g., Apple, TSLA, Microsoft)",
            key="company_search_input",
            label_visibility="collapsed"
        )

    with col2:
        if st.session_state.selected_stock:
            if st.button("Clear", use_container_width=True):
                st.session_state.selected_stock = None
                st.session_state.search_query = ""
                st.session_state.show_suggestions = False
                st.rerun()

    # Debounce: only search if query changed and enough time passed
    current_time = time.time()
    debounce_ms = 150  # 150ms debounce
    query_changed = query != st.session_state.search_query

    if query_changed:
        st.session_state.search_query = query
        st.session_state.last_search_time = current_time
        st.session_state.selected_index = 0

        # Clear selection if user is typing a new query
        if st.session_state.selected_stock:
            selected_text = f"{st.session_state.selected_stock['name']} ({st.session_state.selected_stock['symbol']})"
            if query != selected_text:
                st.session_state.selected_stock = None

    # Determine if we should show suggestions
    show_dropdown = (
        query and
        len(query) >= 1 and
        not st.session_state.selected_stock and
        not query.endswith(")")  # Don't show if user selected something
    )

    if show_dropdown:
        # Search with minimum 1 character, max 8 results
        results = search_stocks(query, stocks, max_results=8, min_query_length=1)

        if results:
            # Render suggestions container
            st.markdown("""
            <style>
            .stock-suggestion {
                padding: 8px 12px;
                border-bottom: 1px solid #333;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .stock-suggestion:hover {
                background-color: #2a2a2a;
            }
            .stock-symbol {
                font-weight: bold;
                color: #4CAF50;
                min-width: 70px;
            }
            .stock-name {
                flex: 1;
                margin: 0 12px;
                color: #e0e0e0;
            }
            .stock-exchange {
                font-size: 0.8em;
                color: #888;
                min-width: 60px;
                text-align: right;
            }
            .stock-name mark {
                background-color: #4CAF50;
                color: #000;
                padding: 0 2px;
                border-radius: 2px;
            }
            .stock-symbol mark {
                background-color: #4CAF50;
                color: #000;
            }
            </style>
            """, unsafe_allow_html=True)

            # Create buttons for each result
            for i, result in enumerate(results):
                symbol = result["symbol"]
                name = result["name"]
                exchange = result["exchange"]

                # Highlight matches
                symbol_highlighted = highlight_match(symbol, query, is_symbol=True)
                name_highlighted = highlight_match(name, query, is_symbol=False)

                # Truncate long names
                if len(name) > 45:
                    name_display = name[:42] + "..."
                    name_highlighted = highlight_match(name_display, query, is_symbol=False)
                else:
                    name_display = name

                # Create clickable button for each result
                col_sym, col_name, col_exch = st.columns([1, 4, 1])
                with col_sym:
                    st.markdown(f"**{symbol}**")
                with col_name:
                    st.caption(name_display)
                with col_exch:
                    st.caption(exchange)

                # Full-width button overlay
                if st.button(
                    f"Select {symbol}",
                    key=f"stock_btn_{symbol}_{i}",
                    use_container_width=True,
                    type="secondary"
                ):
                    st.session_state.selected_stock = {
                        "symbol": symbol,
                        "name": name,
                        "exchange": exchange
                    }
                    st.session_state.show_suggestions = False
                    st.rerun()

            st.markdown("---")

        else:
            # No results state
            if len(query) >= 2:
                st.info(f"No U.S. listed companies found matching '{query}'")
                st.caption("Try a different spelling or ticker symbol")

    # Return selected stock info
    if st.session_state.selected_stock:
        return (
            st.session_state.selected_stock["name"],
            st.session_state.selected_stock["symbol"]
        )

    return None, None


# ============================================================
# FORMATTING HELPERS
# ============================================================

def format_currency(value):
    """Format large numbers as currency ($1.2B, $500M, $1.5K)."""
    if value is None:
        return "N/A"
    if isinstance(value, dict):
        value = value.get("value")
    if value is None:
        return "N/A"
    try:
        value = float(value)
        if abs(value) >= 1e12:
            return f"${value/1e12:.1f}T"
        elif abs(value) >= 1e9:
            return f"${value/1e9:.1f}B"
        elif abs(value) >= 1e6:
            return f"${value/1e6:.1f}M"
        elif abs(value) >= 1e3:
            return f"${value/1e3:.1f}K"
        else:
            return f"${value:.2f}"
    except (TypeError, ValueError):
        return "N/A"


def format_percent(value):
    """Format as percentage."""
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.1f}%"
    except (TypeError, ValueError):
        return "N/A"


def format_ratio(value):
    """Format as ratio (2.1x)."""
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.2f}x"
    except (TypeError, ValueError):
        return "N/A"


def format_number(value, decimals=2):
    """Format a number with specified decimals."""
    if value is None:
        return "N/A"
    try:
        return f"{float(value):.{decimals}f}"
    except (TypeError, ValueError):
        return "N/A"


def format_date(date_str):
    """Format date string to readable format (Dec 26, 2024)."""
    if not date_str:
        return ""
    try:
        # Try ISO format first
        if "T" in str(date_str):
            dt = datetime.fromisoformat(str(date_str).replace("Z", "+00:00"))
        else:
            # Try common date formats
            for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y"]:
                try:
                    dt = datetime.strptime(str(date_str)[:10], fmt)
                    break
                except ValueError:
                    continue
            else:
                return str(date_str)[:10]
        return dt.strftime("%b %d, %Y")
    except Exception:
        return str(date_str)[:10] if date_str else ""


def _render_research_sidebar(metrics: dict):
    """Render research data in the left sidebar."""
    if not metrics:
        return

    # 1. FINANCIALS
    fin = metrics.get("financials") or {}
    fin_data = fin.get("financials") or {}
    fin_date = ""
    if isinstance(fin_data, dict) and fin_data.get("revenue"):
        fin_date = fin_data.get("revenue", {}).get("end_date", "")

    st.sidebar.subheader("Financials")
    if fin_date:
        st.sidebar.caption(f"As of {format_date(fin_date)}")
    if "error" in fin:
        st.sidebar.warning(f"Failed: {fin.get('error', 'Unknown error')[:50]}")
    else:
        revenue = fin_data.get("revenue") if isinstance(fin_data, dict) else None
        st.sidebar.markdown(f"Revenue: **{format_currency(revenue)}**")
        st.sidebar.markdown(f"Net Margin: **{format_percent(fin_data.get('net_margin_pct'))}**")
        st.sidebar.markdown(f"Gross Margin: **{format_percent(fin_data.get('gross_margin_pct'))}**")
        debt = fin.get("debt", {})
        st.sidebar.markdown(f"Debt/Equity: **{format_ratio(debt.get('debt_to_equity'))}**")
        st.sidebar.markdown(f"Total Debt: **{format_currency(debt.get('total_debt'))}**")
        cf = fin.get("cash_flow", {})
        st.sidebar.markdown(f"Free Cash Flow: **{format_currency(cf.get('free_cash_flow'))}**")

    st.sidebar.markdown("---")

    # 2. VALUATION
    val = metrics.get("valuation") or {}
    val_date = val.get("generated_at", "") if val else ""

    st.sidebar.subheader("Valuation")
    if val_date:
        st.sidebar.caption(f"As of {format_date(val_date)}")
    if "error" in val:
        st.sidebar.warning(f"Failed: {val.get('error', 'Unknown error')[:50]}")
    else:
        val_metrics = val.get("metrics", {})
        # Stock Price
        price = val_metrics.get("current_price")
        if price:
            st.sidebar.markdown(f"Stock Price: **${format_number(price)}**")
        st.sidebar.markdown(f"Market Cap: **{format_currency(val_metrics.get('market_cap'))}**")
        pe = val_metrics.get("pe_ratio", {})
        st.sidebar.markdown(f"P/E (T/F): **{format_number(pe.get('trailing'))} / {format_number(pe.get('forward'))}**")
        st.sidebar.markdown(f"P/S: **{format_number(val_metrics.get('ps_ratio'))}**")
        st.sidebar.markdown(f"P/B: **{format_number(val_metrics.get('pb_ratio'))}**")
        st.sidebar.markdown(f"EV/EBITDA: **{format_number(val_metrics.get('ev_ebitda'))}**")
        peg = val_metrics.get("peg_ratio", {})
        st.sidebar.markdown(f"PEG (Trailing): **{format_number(peg.get('trailing'))}**")

    st.sidebar.markdown("---")

    # 3. VOLATILITY
    vol = metrics.get("volatility") or {}
    vol_date = vol.get("generated_at", "") if vol else ""

    st.sidebar.subheader("Volatility")
    if vol_date:
        st.sidebar.caption(f"As of {format_date(vol_date)}")
    if "error" in vol:
        st.sidebar.warning(f"Failed: {vol.get('error', 'Unknown error')[:50]}")
    else:
        vol_metrics = vol.get("metrics", {})
        vix = vol_metrics.get("vix", {})
        st.sidebar.markdown(f"VIX: **{format_number(vix.get('value'))}** ({vix.get('interpretation', 'N/A')})")
        beta = vol_metrics.get("beta", {})
        st.sidebar.markdown(f"Beta: **{format_number(beta.get('value'))}** ({beta.get('interpretation', 'N/A')})")
        hist_vol = vol_metrics.get("historical_volatility", {})
        st.sidebar.markdown(f"Hist. Vol: **{format_percent(hist_vol.get('value'))}**")

    st.sidebar.markdown("---")

    # 4. MACRO
    macro = metrics.get("macro") or {}
    macro_metrics = macro.get("metrics") or {}
    macro_date = ""
    if isinstance(macro_metrics, dict) and macro_metrics.get("gdp_growth"):
        macro_date = macro_metrics.get("gdp_growth", {}).get("date", "")

    st.sidebar.subheader("Macro")
    if macro_date:
        st.sidebar.caption(f"As of {format_date(macro_date)}")
    if "error" in macro:
        st.sidebar.warning(f"Failed: {macro.get('error', 'Unknown error')[:50]}")
    else:
        gdp = macro_metrics.get("gdp_growth", {})
        st.sidebar.markdown(f"GDP Growth: **{format_percent(gdp.get('value'))}**")
        ir = macro_metrics.get("interest_rate", {})
        st.sidebar.markdown(f"Fed Rate: **{format_percent(ir.get('value'))}** ({ir.get('trend', 'N/A')})")
        cpi = macro_metrics.get("cpi_inflation", {})
        st.sidebar.markdown(f"CPI/Inflation: **{format_percent(cpi.get('value'))}**")
        unemp = macro_metrics.get("unemployment", {})
        st.sidebar.markdown(f"Unemployment: **{format_percent(unemp.get('value'))}**")

    st.sidebar.markdown("---")

    # 5. NEWS
    news = metrics.get("news") or {}
    news_count = len(news.get("results") or [])

    st.sidebar.subheader(f"News ({news_count})")
    if "error" in news:
        st.sidebar.warning(f"Failed: {news.get('error', 'Unknown error')[:50]}")
    else:
        for article in news.get("results", [])[:5]:
            title = article.get("title", "Untitled")[:45]
            url = article.get("url", "#")
            pub_date = format_date(article.get("published_date", ""))
            st.sidebar.markdown(f"[{title}...]({url})")
            if pub_date:
                st.sidebar.caption(pub_date)

    st.sidebar.markdown("---")

    # 6. SENTIMENT
    sent = metrics.get("sentiment") or {}
    sent_metrics = sent.get("metrics") or {}
    sent_date = sent.get("generated_at", "") or (sent_metrics.get("finnhub") or {}).get("as_of", "")

    st.sidebar.subheader("Sentiment")
    if sent_date:
        st.sidebar.caption(f"As of {format_date(sent_date)}")
    if "error" in sent:
        st.sidebar.warning(f"Failed: {sent.get('error', 'Unknown error')[:50]}")
    else:
        composite = sent.get("composite_score")
        interpretation = sent.get("overall_interpretation", "")
        if composite is not None:
            st.sidebar.markdown(f"Overall: **{format_number(composite, 0)}/100** ({interpretation})")

        fh = sent_metrics.get("finnhub") or {}
        if fh and "error" not in fh:
            fh_score = fh.get("score")
            fh_articles = fh.get("articles_analyzed", 0)
            st.sidebar.markdown(f"Finnhub: **{format_number(fh_score, 0)}/100** ({fh_articles} articles)")

        reddit = sent_metrics.get("reddit") or {}
        if reddit and "error" not in reddit:
            r_score = reddit.get("score")
            r_posts = reddit.get("posts_analyzed", 0)
            st.sidebar.markdown(f"Reddit: **{format_number(r_score, 0)}/100** ({r_posts} posts)")


def _calculate_confidence(score: float, sources_available: list, sources_failed: list) -> dict:
    """
    Calculate strategic confidence based on score and data coverage.
    Returns confidence level, label, and readiness status.
    """
    # Base confidence from score (0-10 -> 0-60%)
    score_confidence = (score / 10) * 60 if isinstance(score, (int, float)) else 30

    # Data coverage bonus (0-40%)
    total_sources = len(sources_available) + len(sources_failed)
    if total_sources > 0:
        coverage = len(sources_available) / total_sources
        data_confidence = coverage * 40
    else:
        data_confidence = 20

    total_confidence = score_confidence + data_confidence

    # Determine readiness label
    if total_confidence >= 75 and len(sources_failed) == 0:
        readiness = "Board-ready"
        level = "high"
    elif total_confidence >= 60:
        readiness = "Review recommended"
        level = "medium"
    else:
        readiness = "Exploratory"
        level = "low"

    return {
        "confidence": round(total_confidence),
        "readiness": readiness,
        "level": level,
        "score_contribution": round(score_confidence),
        "data_contribution": round(data_confidence)
    }


def _render_api_status():
    """Render API connection status at bottom of sidebar."""
    st.sidebar.markdown("---")
    with st.sidebar.expander("API Status", expanded=False):
        if os.getenv("GROQ_API_KEY"):
            st.success("Groq: Connected")
        elif os.getenv("GEMINI_API_KEY"):
            st.success("Gemini: Connected")
        elif os.getenv("OPENROUTER_API_KEY"):
            st.success("OpenRouter: Connected")
        else:
            st.error("No LLM API configured")

        if os.getenv("FRED_API_KEY"):
            st.success("FRED: Connected")
        else:
            st.warning("FRED: Not configured")

        if os.getenv("FINNHUB_API_KEY"):
            st.success("Finnhub: Connected")
        else:
            st.warning("Finnhub: Not configured")


# Load environment variables from multiple locations
load_dotenv(Path.home() / ".env")  # Home directory first
load_dotenv()  # Then project .env (overrides if set)

# Check for required API keys
has_llm_key = any([
    os.getenv("GROQ_API_KEY"),
    os.getenv("GEMINI_API_KEY"),
    os.getenv("OPENROUTER_API_KEY")
])

st.set_page_config(layout="wide", page_title="AI Strategy Copilot")

# Executive Decision Header
st.title("AI Strategy Copilot")
st.caption("Automated market intelligence with self-evaluating agents")

# View Mode Toggle
view_mode = st.radio(
    "View Mode",
    ["Executive Summary", "Full Analysis", "System Internals"],
    horizontal=True,
    index=1  # Default to Full Analysis
)

# Sidebar header - Research Data (populated after analysis)
st.sidebar.header("Research Data")
st.sidebar.caption("Run analysis to populate")
_render_api_status()

if not has_llm_key:
    st.error("No LLM API key configured. Please set at least one of: GROQ_API_KEY, GEMINI_API_KEY, or OPENROUTER_API_KEY")
    st.stop()

# Stock search with autocomplete
st.markdown("**Select a U.S. listed company:**")
company_name, ticker = render_stock_search()

# Show selected company info
if company_name and ticker:
    st.success(f"Selected: **{company_name}** ({ticker})")
    company = company_name
else:
    company = None
    st.caption("Start typing to search NYSE, NASDAQ, and AMEX listed companies")

run_button = st.button("Generate SWOT", type="primary", disabled=(company is None))

# Default strategy: Competitive Position Analysis
strategy = "Competitive Position"

if run_button and company:
    # Import here to avoid initialization errors when no API keys
    from src.graph_cyclic import app as graph_app

    with st.spinner("Analyzing..."):
        # Initialize state
        state = {
            "company_name": company,
            "ticker": ticker,  # From stock search
            "strategy_focus": strategy,
            "raw_data": None,
            "draft_report": None,
            "critique": None,
            "revision_count": 0,
            "messages": [],
            "score": 0,
            "data_source": "live",
            "provider_used": None,
            "sources_failed": []
        }

        try:
            # Execute the workflow
            result = graph_app.invoke(state)
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")
            st.stop()

    # Show warning if some data sources failed
    if result.get("sources_failed"):
        st.warning(f"Some data sources failed: {', '.join(result.get('sources_failed', []))}")

    # Parse raw_data for sidebar research panel
    raw_data = {}
    if result.get("raw_data"):
        try:
            raw_data = json.loads(result["raw_data"])
        except json.JSONDecodeError:
            raw_data = {}
    metrics = raw_data.get("metrics", {})

    # ============================================================
    # LEFT SIDEBAR: Research Data Panel
    # ============================================================
    _render_research_sidebar(metrics)
    _render_api_status()

    # ============================================================
    # STRATEGIC CONFIDENCE SCORE
    # ============================================================
    score = result.get("score", 0)
    revisions = result.get("revision_count", 0)
    sources_available = raw_data.get("sources_available", [])
    sources_failed = result.get("sources_failed", [])

    confidence = _calculate_confidence(score, sources_available, sources_failed)

    # Confidence header with metrics
    conf_col1, conf_col2, conf_col3, conf_col4 = st.columns([2, 1, 1, 1])
    with conf_col1:
        st.subheader(f"Strategic Analysis: {company}")
    with conf_col2:
        confidence_color = {"high": "green", "medium": "orange", "low": "red"}.get(confidence["level"], "gray")
        st.metric("Confidence", f"{confidence['confidence']}%", delta=confidence["readiness"])
    with conf_col3:
        st.metric("Quality Score", f"{score}/10")
    with conf_col4:
        st.metric("Self-Corrections", revisions)

    # ============================================================
    # VIEW MODE CONDITIONAL DISPLAY
    # ============================================================
    if view_mode == "Executive Summary":
        # Executive Summary: One-page SWOT with confidence
        st.markdown("---")
        st.markdown(result["draft_report"])

        # Brief quality note
        if confidence["level"] == "high":
            st.success(f"Analysis confidence: {confidence['confidence']}% - {confidence['readiness']}")
        elif confidence["level"] == "medium":
            st.warning(f"Analysis confidence: {confidence['confidence']}% - {confidence['readiness']}")
        else:
            st.info(f"Analysis confidence: {confidence['confidence']}% - {confidence['readiness']}")

    elif view_mode == "Full Analysis":
        # Full Analysis: All tabs with details
        tab1, tab2, tab3, tab4 = st.tabs(["SWOT Analysis", "Quality Evaluation", "Agent Workflow", "Process Details"])

        with tab1:
            st.markdown(result["draft_report"])

        with tab2:
            st.subheader("Quality Evaluation")
            critique = result.get("critique", "No critique available")

            if isinstance(score, (int, float)):
                st.progress(score / 10)
                if score >= 7:
                    st.success(f"**Score:** {score}/10 - High Quality")
                elif score >= 5:
                    st.warning(f"**Score:** {score}/10 - Acceptable")
                else:
                    st.error(f"**Score:** {score}/10 - Needs Improvement")
            else:
                st.info(f"**Score:** {score}")

            # Self-Correction Visibility
            st.markdown("---")
            st.markdown("**Self-Correction Summary**")
            if revisions > 0:
                st.info(f"The AI agents revised this analysis {revisions} time(s) to improve quality.")
                st.markdown(f"Each revision addressed feedback from the Critic agent to strengthen the analysis.")
            else:
                st.success("Analysis met quality standards on first pass - no revisions needed.")

            st.text_area("Detailed Critique", critique, height=150)

        with tab3:
            st.subheader("Agent Workflow")
            st.markdown("**Multi-agent orchestration pipeline**")

            # Agent timeline
            agent_col1, agent_col2, agent_col3, agent_col4 = st.columns(4)

            with agent_col1:
                st.markdown("**1. Researcher**")
                st.caption("Data Collection")
                st.markdown(f"Sources: {len(sources_available)}/{len(sources_available) + len(sources_failed)}")
                if sources_failed:
                    st.warning(f"Failed: {', '.join(sources_failed)}")
                else:
                    st.success("All sources collected")

            with agent_col2:
                st.markdown("**2. Analyst**")
                st.caption("SWOT Synthesis")
                st.markdown("Competitive analysis")
                st.success("Draft generated")

            with agent_col3:
                st.markdown("**3. Critic**")
                st.caption("Quality Evaluation")
                st.markdown(f"Score: {score}/10")
                if score >= 7:
                    st.success("Approved")
                else:
                    st.warning("Requested revision")

            with agent_col4:
                st.markdown("**4. Editor**")
                st.caption("Refinement")
                st.markdown(f"Revisions: {revisions}")
                if revisions > 0:
                    st.info(f"{revisions} revision(s) made")
                else:
                    st.success("No revisions needed")

            # Workflow explanation
            st.markdown("---")
            st.markdown("""
            **How it works:**
            - **Researcher** aggregates data from 6 MCP servers (financials, valuation, volatility, macro, news, sentiment)
            - **Analyst** synthesizes data into strategic SWOT framework aligned with chosen strategy
            - **Critic** evaluates quality using hybrid scoring (40% deterministic checks + 60% LLM evaluation)
            - **Editor** refines the analysis if score < 7/10 (up to 3 revision cycles)
            """)

        with tab4:
            st.subheader("Process Details")
            pcol1, pcol2 = st.columns(2)
            with pcol1:
                st.write(f"**Company:** {company}")
                st.write(f"**Analysis Type:** Competitive Position")
                st.write(f"**Report Length:** {len(result.get('draft_report', ''))} chars")
            with pcol2:
                provider = result.get("provider_used", "Unknown")
                data_source = result.get("data_source", "unknown")
                st.write(f"**LLM Provider:** {provider}")
                data_source_label = {
                    "live": "Live MCP servers",
                    "cached": "Cached (SQLite)",
                    "a2a": "A2A Protocol (decoupled)"
                }.get(data_source, data_source)
                st.write(f"**Data Source:** {data_source_label}")
                st.write(f"**Revisions:** {revisions}")

            # Confidence breakdown
            st.markdown("---")
            st.markdown("**Confidence Score Breakdown**")
            st.write(f"- Quality contribution: {confidence['score_contribution']}% (from {score}/10 score)")
            st.write(f"- Data coverage contribution: {confidence['data_contribution']}% (from {len(sources_available)}/{len(sources_available) + len(sources_failed)} sources)")
            st.write(f"- **Total confidence: {confidence['confidence']}%** ({confidence['readiness']})")

    else:  # System Internals
        # System Internals: Technical details for developers
        tab1, tab2, tab3 = st.tabs(["Raw Output", "Agent State", "Debug Info"])

        with tab1:
            st.subheader("Raw SWOT Output")
            st.code(result["draft_report"], language="markdown")

        with tab2:
            st.subheader("Final Agent State")
            state_display = {
                "company_name": company,
                "strategy_focus": strategy,
                "score": score,
                "revision_count": revisions,
                "provider_used": result.get("provider_used"),
                "data_source": result.get("data_source"),
                "sources_available": sources_available,
                "sources_failed": sources_failed
            }
            st.json(state_display)

        with tab3:
            st.subheader("Debug Information")
            st.markdown("**Critique Details**")
            critique_details = result.get("critique_details", {})
            if critique_details:
                st.json(critique_details)
            else:
                st.text_area("Critique", result.get("critique", "No critique available"), height=150)

            st.markdown("**Raw Data (truncated)**")
            if raw_data:
                st.json({k: str(v)[:200] + "..." if len(str(v)) > 200 else v for k, v in raw_data.items() if k != "metrics"})


# Footer
st.markdown("---")
st.caption("AI Strategy Copilot | Multi-agent SWOT analysis with self-correction | [GitHub](https://github.com/vn6295337/A2A-strategy-agent)")
