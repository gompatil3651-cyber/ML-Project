import streamlit as st
import pandas as pd
from utils.api_client import api_client, TICKERS
from components.recommendation_card import render_recommendation_card
from components.charts import render_candlestick_chart, render_rsi_chart
from components.sentiment_view import render_sentiment_section

# Page Configuration
st.set_page_config(
    page_title="Stock Insight | Intelligent Recommendation System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Light Theme CSS
st.markdown("""
<style>
    /* Global Background and Typography */
    .main {
        background-color: #F8FAFC;
    }
    h1, h2, h3, h4 {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0F172A;
    }
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    div[data-testid="stMetricLabel"] {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #64748B !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px !important;
        font-weight: 800 !important;
        color: #0F172A !important;
    }
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #F1F5F9;
        padding: 6px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 18px;
        font-weight: 600;
        color: #475569;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #2563EB !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

# 150 Target Stock Universe Metadata
STOCK_UNIVERSE = {
    # Technology (30)
    "AAPL": {"name": "Apple Inc.", "sector": "Technology"},
    "MSFT": {"name": "Microsoft Corporation", "sector": "Technology"},
    "GOOGL": {"name": "Alphabet Inc. (Google)", "sector": "Technology"},
    "AMZN": {"name": "Amazon.com, Inc.", "sector": "Technology"},
    "NVDA": {"name": "Nvidia Corporation", "sector": "Technology"},
    "META": {"name": "Meta Platforms, Inc.", "sector": "Technology"},
    "AVGO": {"name": "Broadcom Inc.", "sector": "Technology"},
    "ORCL": {"name": "Oracle Corporation", "sector": "Technology"},
    "CRM": {"name": "Salesforce, Inc.", "sector": "Technology"},
    "AMD": {"name": "Advanced Micro Devices, Inc.", "sector": "Technology"},
    "ADBE": {"name": "Adobe Inc.", "sector": "Technology"},
    "CSCO": {"name": "Cisco Systems, Inc.", "sector": "Technology"},
    "IBM": {"name": "International Business Machines", "sector": "Technology"},
    "QCOM": {"name": "Qualcomm Inc.", "sector": "Technology"},
    "TXN": {"name": "Texas Instruments Inc.", "sector": "Technology"},
    "INTU": {"name": "Intuit Inc.", "sector": "Technology"},
    "AMAT": {"name": "Applied Materials, Inc.", "sector": "Technology"},
    "MU": {"name": "Micron Technology, Inc.", "sector": "Technology"},
    "LRCX": {"name": "Lam Research Corporation", "sector": "Technology"},
    "NOW": {"name": "ServiceNow, Inc.", "sector": "Technology"},
    "PANW": {"name": "Palo Alto Networks, Inc.", "sector": "Technology"},
    "SNPS": {"name": "Synopsys, Inc.", "sector": "Technology"},
    "CDNS": {"name": "Cadence Design Systems, Inc.", "sector": "Technology"},
    "ADI": {"name": "Analog Devices, Inc.", "sector": "Technology"},
    "KLAC": {"name": "KLA Corporation", "sector": "Technology"},
    "ANET": {"name": "Arista Networks, Inc.", "sector": "Technology"},
    "APH": {"name": "Amphenol Corporation", "sector": "Technology"},
    "MSI": {"name": "Motorola Solutions, Inc.", "sector": "Technology"},
    "FTNT": {"name": "Fortinet, Inc.", "sector": "Technology"},
    "PLTR": {"name": "Palantir Technologies Inc.", "sector": "Technology"},

    # Financials (20)
    "JPM": {"name": "JPMorgan Chase & Co.", "sector": "Financials"},
    "BAC": {"name": "Bank of America Corporation", "sector": "Financials"},
    "WFC": {"name": "Wells Fargo & Company", "sector": "Financials"},
    "GS": {"name": "The Goldman Sachs Group, Inc.", "sector": "Financials"},
    "MS": {"name": "Morgan Stanley", "sector": "Financials"},
    "C": {"name": "Citigroup Inc.", "sector": "Financials"},
    "AXP": {"name": "American Express Company", "sector": "Financials"},
    "BLK": {"name": "BlackRock, Inc.", "sector": "Financials"},
    "SCHW": {"name": "The Charles Schwab Corporation", "sector": "Financials"},
    "USB": {"name": "U.S. Bancorp", "sector": "Financials"},
    "PNC": {"name": "The PNC Financial Services Group", "sector": "Financials"},
    "TFC": {"name": "Truist Financial Corporation", "sector": "Financials"},
    "COF": {"name": "Capital One Financial Corporation", "sector": "Financials"},
    "CB": {"name": "Chubb Limited", "sector": "Financials"},
    "CME": {"name": "CME Group Inc.", "sector": "Financials"},
    "ICE": {"name": "Intercontinental Exchange, Inc.", "sector": "Financials"},
    "SPGI": {"name": "S&P Global Inc.", "sector": "Financials"},
    "MCO": {"name": "Moody's Corporation", "sector": "Financials"},
    "AON": {"name": "Aon plc", "sector": "Financials"},
    "MMC": {"name": "Marsh & McLennan Companies", "sector": "Financials"},

    # Healthcare (20)
    "LLY": {"name": "Eli Lilly and Company", "sector": "Healthcare"},
    "JNJ": {"name": "Johnson & Johnson", "sector": "Healthcare"},
    "ABBV": {"name": "AbbVie Inc.", "sector": "Healthcare"},
    "MRK": {"name": "Merck & Co., Inc.", "sector": "Healthcare"},
    "PFE": {"name": "Pfizer Inc.", "sector": "Healthcare"},
    "ABT": {"name": "Abbott Laboratories", "sector": "Healthcare"},
    "TMO": {"name": "Thermo Fisher Scientific Inc.", "sector": "Healthcare"},
    "DHR": {"name": "Danaher Corporation", "sector": "Healthcare"},
    "AMGN": {"name": "Amgen Inc.", "sector": "Healthcare"},
    "GILD": {"name": "Gilead Sciences, Inc.", "sector": "Healthcare"},
    "ISRG": {"name": "Intuitive Surgical, Inc.", "sector": "Healthcare"},
    "VRTX": {"name": "Vertex Pharmaceuticals Inc.", "sector": "Healthcare"},
    "REGN": {"name": "Regeneron Pharmaceuticals, Inc.", "sector": "Healthcare"},
    "BSX": {"name": "Boston Scientific Corporation", "sector": "Healthcare"},
    "SYK": {"name": "Stryker Corporation", "sector": "Healthcare"},
    "MDT": {"name": "Medtronic plc", "sector": "Healthcare"},
    "ELV": {"name": "Elevance Health, Inc.", "sector": "Healthcare"},
    "CI": {"name": "The Cigna Group", "sector": "Healthcare"},
    "HCA": {"name": "HCA Healthcare, Inc.", "sector": "Healthcare"},
    "ZTS": {"name": "Zoetis Inc.", "sector": "Healthcare"},

    # Consumer (20)
    "WMT": {"name": "Walmart Inc.", "sector": "Consumer"},
    "COST": {"name": "Costco Wholesale Corporation", "sector": "Consumer"},
    "HD": {"name": "The Home Depot, Inc.", "sector": "Consumer"},
    "LOW": {"name": "Lowe's Companies, Inc.", "sector": "Consumer"},
    "MCD": {"name": "McDonald's Corporation", "sector": "Consumer"},
    "NKE": {"name": "NIKE, Inc.", "sector": "Consumer"},
    "TJX": {"name": "The TJX Companies, Inc.", "sector": "Consumer"},
    "SBUX": {"name": "Starbucks Corporation", "sector": "Consumer"},
    "TGT": {"name": "Target Corporation", "sector": "Consumer"},
    "BKNG": {"name": "Booking Holdings Inc.", "sector": "Consumer"},
    "MAR": {"name": "Marriott International, Inc.", "sector": "Consumer"},
    "CMG": {"name": "Chipotle Mexican Grill, Inc.", "sector": "Consumer"},
    "ORLY": {"name": "O'Reilly Automotive, Inc.", "sector": "Consumer"},
    "AZO": {"name": "AutoZone, Inc.", "sector": "Consumer"},
    "ROST": {"name": "Ross Stores, Inc.", "sector": "Consumer"},
    "YUM": {"name": "Yum! Brands, Inc.", "sector": "Consumer"},
    "CL": {"name": "Colgate-Palmolive Company", "sector": "Consumer"},
    "PG": {"name": "The Procter & Gamble Company", "sector": "Consumer"},
    "KO": {"name": "The Coca-Cola Company", "sector": "Consumer"},
    "PEP": {"name": "PepsiCo, Inc.", "sector": "Consumer"},

    # Energy (10)
    "XOM": {"name": "Exxon Mobil Corporation", "sector": "Energy"},
    "CVX": {"name": "Chevron Corporation", "sector": "Energy"},
    "COP": {"name": "ConocoPhillips", "sector": "Energy"},
    "SLB": {"name": "SLB (Schlumberger)", "sector": "Energy"},
    "EOG": {"name": "EOG Resources, Inc.", "sector": "Energy"},
    "PSX": {"name": "Phillips 66", "sector": "Energy"},
    "VLO": {"name": "Valero Energy Corporation", "sector": "Energy"},
    "OXY": {"name": "Occidental Petroleum Corporation", "sector": "Energy"},
    "FANG": {"name": "Diamondback Energy, Inc.", "sector": "Energy"},
    "KMI": {"name": "Kinder Morgan, Inc.", "sector": "Energy"},

    # Industrials (20)
    "CAT": {"name": "Caterpillar Inc.", "sector": "Industrials"},
    "DE": {"name": "Deere & Company", "sector": "Industrials"},
    "GE": {"name": "GE Aerospace", "sector": "Industrials"},
    "HON": {"name": "Honeywell International Inc.", "sector": "Industrials"},
    "ETN": {"name": "Eaton Corporation plc", "sector": "Industrials"},
    "PH": {"name": "Parker-Hannifin Corporation", "sector": "Industrials"},
    "EMR": {"name": "Emerson Electric Co.", "sector": "Industrials"},
    "UPS": {"name": "United Parcel Service, Inc.", "sector": "Industrials"},
    "UNP": {"name": "Union Pacific Corporation", "sector": "Industrials"},
    "RTX": {"name": "RTX Corporation", "sector": "Industrials"},
    "LMT": {"name": "Lockheed Martin Corporation", "sector": "Industrials"},
    "NOC": {"name": "Northrop Grumman Corporation", "sector": "Industrials"},
    "GD": {"name": "General Dynamics Corporation", "sector": "Industrials"},
    "WM": {"name": "Waste Management, Inc.", "sector": "Industrials"},
    "CSX": {"name": "CSX Corporation", "sector": "Industrials"},
    "NSC": {"name": "Norfolk Southern Corporation", "sector": "Industrials"},
    "FDX": {"name": "FedEx Corporation", "sector": "Industrials"},
    "MMM": {"name": "3M Company", "sector": "Industrials"},
    "ITW": {"name": "Illinois Tool Works Inc.", "sector": "Industrials"},
    "CARR": {"name": "Carrier Global Corporation", "sector": "Industrials"},

    # Real Estate (10)
    "AMT": {"name": "American Tower Corporation", "sector": "Real Estate"},
    "PLD": {"name": "Prologis, Inc.", "sector": "Real Estate"},
    "EQIX": {"name": "Equinix, Inc.", "sector": "Real Estate"},
    "PSA": {"name": "Public Storage", "sector": "Real Estate"},
    "SPG": {"name": "Simon Property Group, Inc.", "sector": "Real Estate"},
    "O": {"name": "Realty Income Corporation", "sector": "Real Estate"},
    "CCI": {"name": "Crown Castle Inc.", "sector": "Real Estate"},
    "DLR": {"name": "Digital Realty Trust, Inc.", "sector": "Real Estate"},
    "WELL": {"name": "Welltower Inc.", "sector": "Real Estate"},
    "AVB": {"name": "AvalonBay Communities, Inc.", "sector": "Real Estate"},

    # Utilities (10)
    "NEE": {"name": "NextEra Energy, Inc.", "sector": "Utilities"},
    "CEG": {"name": "Constellation Energy Corporation", "sector": "Utilities"},
    "SO": {"name": "The Southern Company", "sector": "Utilities"},
    "DUK": {"name": "Duke Energy Corporation", "sector": "Utilities"},
    "AEP": {"name": "American Electric Power Company", "sector": "Utilities"},
    "SRE": {"name": "Sempra", "sector": "Utilities"},
    "VST": {"name": "Vistra Corp.", "sector": "Utilities"},
    "EXC": {"name": "Exelon Corporation", "sector": "Utilities"},
    "D": {"name": "Dominion Energy, Inc.", "sector": "Utilities"},
    "PEG": {"name": "Public Service Enterprise Group", "sector": "Utilities"},

    # Communication Services (10)
    "TMUS": {"name": "T-Mobile US, Inc.", "sector": "Communication Services"},
    "VZ": {"name": "Verizon Communications Inc.", "sector": "Communication Services"},
    "T": {"name": "AT&T Inc.", "sector": "Communication Services"},
    "CMCSA": {"name": "Comcast Corporation", "sector": "Communication Services"},
    "CHTR": {"name": "Charter Communications, Inc.", "sector": "Communication Services"},
    "DIS": {"name": "The Walt Disney Company", "sector": "Communication Services"},
    "NFLX": {"name": "Netflix, Inc.", "sector": "Communication Services"},
    "FOXA": {"name": "Fox Corporation", "sector": "Communication Services"},
    "EA": {"name": "Electronic Arts Inc.", "sector": "Communication Services"},
    "TTWO": {"name": "Take-Two Interactive Software", "sector": "Communication Services"},
}

SECTORS = [
    "All Sectors (150 Stocks)",
    "Technology",
    "Financials",
    "Healthcare",
    "Consumer",
    "Energy",
    "Industrials",
    "Real Estate",
    "Utilities",
    "Communication Services"
]

# Sidebar Configuration
with st.sidebar:
    st.markdown("<h2 style='font-size: 22px; font-weight: 800; color: #1E293B; margin-bottom: 4px;'>📈 Stock Insight</h2>", unsafe_allow_html=True)
    st.markdown("<span style='font-size: 12px; color: #64748B;'>Intelligent Stock Analysis (150 S&P Leaders)</span>", unsafe_allow_html=True)
    st.divider()

    st.subheader("Select Universe Asset")
    selected_sector = st.selectbox("Sector Filter", options=SECTORS, index=0)

    if selected_sector == "All Sectors (150 Stocks)":
        available_tickers = list(STOCK_UNIVERSE.keys())
    else:
        available_tickers = [t for t, meta in STOCK_UNIVERSE.items() if meta["sector"] == selected_sector]

    # Default to NVDA if available, else first
    def_idx = available_tickers.index("NVDA") if "NVDA" in available_tickers else 0
    selected_ticker = st.selectbox(
        "Target Stock",
        options=available_tickers,
        index=def_idx,
        format_func=lambda x: f"{x} - {STOCK_UNIVERSE.get(x, {}).get('name', '')}"
    )

    st.subheader("Chart Horizon")
    timeframe = st.select_slider(
        "Historical Period",
        options=["1mo", "3mo", "6mo", "1y", "2y"],
        value="1y"
    )

    st.divider()

    # System Health Badge
    st.markdown("#### System Health Status")
    health = api_client.get_system_health()
    db_status = health.get("database", {}).get("status", "CONNECTED")
    py_status = health.get("python_microservice", {}).get("status", "UP")
    if py_status == "UP":
        py_color = "#10B981"
        py_label = "● Online (Port 8000)"
    elif "FALLBACK" in py_status:
        py_color = "#F59E0B"
        py_label = "● Resilient Fallback Active"
    else:
        py_color = "#EF4444"
        py_label = f"● {py_status}"

    db_color = "#10B981" if "CONNECTED" in db_status else "#EF4444"

    st.html(f"""<div style="font-size: 13px; line-height: 1.8;">
<div>Backend API: <span style="color: #10B981; font-weight: 700;">● Online (Port 5000)</span></div>
<div>Database (MongoDB): <span style="color: {db_color}; font-weight: 700;">● {db_status}</span></div>
<div>ML Microservice: <span style="color: {py_color}; font-weight: 700;">{py_label}</span></div>
<div style="margin-top: 6px; font-size: 11px; color: #64748B;">Active Universe: <strong>150 Target Assets</strong></div>
</div>""")

# Main Application Layout
stock_meta = STOCK_UNIVERSE.get(selected_ticker, {"name": selected_ticker, "sector": "Market"})
st.html(f"""<div style="display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 20px;">
<div>
<h1 style="margin: 0; font-size: 32px; font-weight: 900; letter-spacing: -0.02em; color: #0F172A;">{selected_ticker} &middot; {stock_meta['name']}</h1>
<p style="margin: 4px 0 0 0; color: #64748B; font-size: 14px;"><strong>Sector:</strong> {stock_meta['sector']} &bull; Technical indicators, FinBERT news sentiment, and XGBoost next-session recommendation</p>
</div>
</div>""")

# Fetch Data in Parallel / Sequence
with st.spinner(f"Analyzing {selected_ticker} via Python ML Pipeline & Node Backend..."):
    technicals = api_client.get_ticker_technicals(selected_ticker)
    prediction = api_client.get_ticker_prediction(selected_ticker)
    sentiment = api_client.get_news_sentiment(selected_ticker, limit=15)
    history_resp = api_client.get_historical_candles(selected_ticker, period=timeframe)
    history_data = history_resp.get("data", [])

# Top Metric Cards
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    latest_close = technicals.get("latest_close", 0.0)
    daily_ret = technicals.get("daily_return", 0.0) * 100
    st.metric("Latest Close", f"${latest_close:,.2f}", f"{daily_ret:+.2f}%")

with col2:
    ret_7d = technicals.get("return_7d", 0.0) * 100
    st.metric("7-Day Return", f"{ret_7d:+.2f}%", delta=f"{ret_7d:+.2f}%")

with col3:
    ret_30d = technicals.get("return_30d", 0.0) * 100
    st.metric("30-Day Return", f"{ret_30d:+.2f}%", delta=f"{ret_30d:+.2f}%")

with col4:
    rsi = technicals.get("rsi_14", 50.0)
    rsi_state = "Overbought" if rsi > 70 else ("Oversold" if rsi < 30 else "Neutral")
    st.metric("RSI (14)", f"{rsi:.1f}", rsi_state)

with col5:
    vol = technicals.get("volatility_20", 0.20) * 100
    st.metric("20-Day Volatility", f"{vol:.1f}%", "Annualized")

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

# Main AI Recommendation Card
render_recommendation_card(prediction)

# Tabbed Analytics Views
tab1, tab2, tab3 = st.tabs(["📊 Interactive Technical Charts", "📰 FinBERT News Sentiment", "🌐 S&P 150 Universe Matrix"])

with tab1:
    col_chart, col_stats = st.columns([3, 1])
    
    with col_chart:
        fig_candle = render_candlestick_chart(history_data, selected_ticker)
        st.plotly_chart(fig_candle, use_container_width=True)

        fig_rsi = render_rsi_chart(history_data)
        st.plotly_chart(fig_rsi, use_container_width=True)

    with col_stats:
        st.markdown("<h4 style='font-size: 16px; font-weight: 700; color: #1E293B;'>Indicator Snapshot</h4>", unsafe_allow_html=True)
        stats_df = pd.DataFrame([
            {"Indicator": "SMA 5", "Value": f"${technicals.get('sma_5', 0):,.2f}"},
            {"Indicator": "SMA 10", "Value": f"${technicals.get('sma_10', 0):,.2f}"},
            {"Indicator": "SMA 20", "Value": f"${technicals.get('sma_20', 0):,.2f}"},
            {"Indicator": "EMA 5", "Value": f"${technicals.get('ema_5', 0):,.2f}"},
            {"Indicator": "EMA 10", "Value": f"${technicals.get('ema_10', 0):,.2f}"},
            {"Indicator": "EMA 20", "Value": f"${technicals.get('ema_20', 0):,.2f}"},
            {"Indicator": "10-Day Momentum", "Value": f"${technicals.get('momentum_10', 0):+,.2f}"},
            {"Indicator": "Volume", "Value": f"{technicals.get('volume', 0):,}"},
        ])
        st.dataframe(stats_df, hide_index=True, use_container_width=True)

        st.html("""<div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px; margin-top: 14px; font-size: 13px; color: #475569; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
<strong style="color: #0F172A;">💡 Non-Technical Note:</strong>
<p style="margin: 4px 0 0 0; line-height: 1.4;">When price trades above both SMA 20 and EMA 20 while RSI stays between 40&ndash;65, bullish momentum is typically reinforced.</p>
</div>""")

with tab2:
    render_sentiment_section(sentiment)

with tab3:
    st.markdown("<h4 style='font-size: 18px; font-weight: 700; margin-bottom: 8px;'>Target Universe Comparison Matrix (150 Market Leaders)</h4>", unsafe_allow_html=True)
    st.caption("Comprehensive real-time recommendations, sentiment compound scores, and volatility metrics across sectors.")

    with st.spinner("Fetching universe comparative matrix..."):
        universe_recs = api_client.get_universe_overview()

    if universe_recs:
        matrix_rows = []
        for sym in TICKERS:
            data = universe_recs.get(sym) or api_client.get_ticker_prediction(sym)
            tech = data.get("technical_summary", {})
            sent = data.get("sentiment_summary", {})
            meta = STOCK_UNIVERSE.get(sym, {"name": sym, "sector": "Market"})
            matrix_rows.append({
                "Ticker": sym,
                "Company": meta["name"],
                "Sector": meta["sector"],
                "Latest Price": f"${tech.get('latest_close', 0):,.2f}",
                "Daily Return": f"{tech.get('daily_return', 0)*100:+.2f}%",
                "RSI (14)": f"{tech.get('rsi_14', 0):.1f}",
                "Sentiment Score": f"{sent.get('Sentiment_Score', 0):+.3f}",
                "AI Recommendation": data.get("prediction", "HOLD"),
                "Confidence": f"{float(data.get('confidence', 0))*100:.1f}%"
            })
        
        matrix_df = pd.DataFrame(matrix_rows)

        # Filters for Matrix
        col_m1, col_m2 = st.columns([2, 1])
        with col_m1:
            search_query = st.text_input("🔍 Search Matrix (by Ticker, Company, or Sector)", "").strip().lower()
        with col_m2:
            rec_filter = st.selectbox("Filter by Recommendation", ["All Recommendations", "BUY", "HOLD", "WAIT"], index=0)

        filtered_df = matrix_df.copy()
        if search_query:
            filtered_df = filtered_df[
                filtered_df["Ticker"].str.lower().str.contains(search_query) |
                filtered_df["Company"].str.lower().str.contains(search_query) |
                filtered_df["Sector"].str.lower().str.contains(search_query)
            ]
        if rec_filter != "All Recommendations":
            filtered_df = filtered_df[filtered_df["AI Recommendation"] == rec_filter]

        # Summary KPIs
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Total Shown", len(filtered_df))
        k2.metric("BUY Signals", len(filtered_df[filtered_df["AI Recommendation"] == "BUY"]))
        k3.metric("HOLD Signals", len(filtered_df[filtered_df["AI Recommendation"] == "HOLD"]))
        k4.metric("WAIT Signals", len(filtered_df[filtered_df["AI Recommendation"] == "WAIT"]))

        st.dataframe(filtered_df, hide_index=True, use_container_width=True)
    else:
        st.info("Universe recommendations loading or initializing.")
