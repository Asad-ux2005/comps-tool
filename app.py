import os
import time
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_KEY = st.secrets.get("API_KEY") or os.getenv("API_KEY")
BASE = "https://www.alphavantage.co/query"

st.set_page_config(page_title="Comps Tool", layout="wide", page_icon="📊")

st.markdown("""
<style>
    .stApp { background-color: #0d1b2a; }
    h1, h2, h3 { color: #ffffff; font-family: 'Arial', sans-serif; letter-spacing: 1px; }
    p, label, div { color: #cbd5e1; font-family: 'Arial', sans-serif; }
    .stButton>button {
        background-color: #c9a84c;
        color: #0d1b2a;
        font-weight: bold;
        font-family: 'Arial', sans-serif;
        border: none;
        padding: 10px 24px;
        border-radius: 4px;
        width: 100%;
        font-size: 14px;
        letter-spacing: 1px;
    }
    .stButton>button:hover { background-color: #e8c46a; color: #0d1b2a; }
    .stTextInput>div>div>input {
        background-color: #1b2d45;
        color: #ffffff;
        border: 1px solid #c9a84c;
        font-family: 'Arial', sans-serif;
        border-radius: 4px;
    }
    .metric-card {
        background-color: #1b2d45;
        border: 1px solid #c9a84c;
        border-radius: 6px;
        padding: 20px;
        text-align: center;
        margin-bottom: 10px;
    }
    .metric-value { font-size: 26px; color: #c9a84c; font-weight: bold; font-family: 'Arial'; }
    .metric-label { font-size: 11px; color: #94a3b8; font-family: 'Arial'; letter-spacing: 1px; margin-top: 4px; }
    .divider { border-top: 1px solid #c9a84c; margin: 20px 0; opacity: 0.4; }
    div[data-testid="stDataFrame"] { border: 1px solid #1b2d45; border-radius: 6px; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    .stDownloadButton>button {
        background-color: transparent;
        color: #c9a84c;
        border: 1px solid #c9a84c;
        font-family: 'Arial', sans-serif;
        border-radius: 4px;
        letter-spacing: 1px;
    }
    .stDownloadButton>button:hover { background-color: #c9a84c; color: #0d1b2a; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────
st.markdown("## 📊 COMPS TOOL")
st.markdown("**Automated Comparable Company Analysis**")
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown("Enter up to 5 US stock tickers separated by commas &nbsp;·&nbsp; e.g. `WMT, COST, TGT, KR, SFM`")

col1, col2 = st.columns([4, 1])
with col1:
    ticker_input = st.text_input("", value="WMT, COST, TGT, KR, SFM", label_visibility="collapsed")
with col2:
    run = st.button("RUN ANALYSIS")

# ── API helpers ──────────────────────────────────────────────────
def get_overview(ticker):
    r = requests.get(BASE, params={"function": "OVERVIEW", "symbol": ticker, "apikey": API_KEY})
    return r.json()

def get_income(ticker):
    r = requests.get(BASE, params={"function": "INCOME_STATEMENT", "symbol": ticker, "apikey": API_KEY})
    data = r.json()
    return (data.get("annualReports") or [{}])[0]

def get_balance(ticker):
    r = requests.get(BASE, params={"function": "BALANCE_SHEET", "symbol": ticker, "apikey": API_KEY})
    data = r.json()
    return (data.get("annualReports") or [{}])[0]

def safe_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0

# ── Main logic ───────────────────────────────────────────────────
if run:
    tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()][:5]
    rows = []
    progress = st.progress(0)
    status = st.empty()

    for i, ticker in enumerate(tickers):
        status.markdown(f"⏳ Fetching **{ticker}** ({i+1}/{len(tickers)})...")

        overview = get_overview(ticker)
        time.sleep(12)
        income = get_income(ticker)
        time.sleep(12)
        balance = get_balance(ticker)
        time.sleep(12)

        if not overview or "Symbol" not in overview:
            status.warning(f"No data found for {ticker} — skipping")
            continue

        market_cap = safe_float(overview.get("MarketCapitalization", 0))
        total_debt = safe_float(balance.get("shortLongTermDebtTotal", 0))
        cash       = safe_float(balance.get("cashAndCashEquivalentsAtCarryingValue", 0))
        ev         = market_cap + total_debt - cash
        revenue    = safe_float(income.get("totalRevenue", 0))
        ebitda     = safe_float(income.get("ebitda", 0))
        net_income = safe_float(income.get("netIncome", 0))
        pe_ratio   = safe_float(overview.get("PERatio", 0))
        pb_ratio   = safe_float(overview.get("PriceToBookRatio", 0))

        rows.append({
            "Ticker":          ticker,
            "Market Cap ($m)": round(market_cap / 1e6, 1),
            "EV ($m)":         round(ev / 1e6, 1),
            "Revenue ($m)":    round(revenue / 1e6, 1),
            "EBITDA ($m)":     round(ebitda / 1e6, 1),
            "EV/Revenue":      round(ev / revenue, 2) if revenue else "N/A",
            "EV/EBITDA":       round(ev / ebitda, 2) if ebitda else "N/A",
            "P/E Ratio":       pe_ratio or "N/A",
            "P/B Ratio":       pb_ratio or "N/A",
            "Net Income ($m)": round(net_income / 1e6, 1),
        })

        progress.progress((i + 1) / len(tickers))

    status.empty()
    progress.empty()

    if rows:
        df = pd.DataFrame(rows)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("### SUMMARY METRICS")

        m1, m2, m3, m4 = st.columns(4)
        avg_ev_ebitda = pd.to_numeric(df["EV/EBITDA"], errors="coerce").mean()
        avg_ev_rev    = pd.to_numeric(df["EV/Revenue"], errors="coerce").mean()
        avg_pe        = pd.to_numeric(df["P/E Ratio"],  errors="coerce").mean()
        avg_pb        = pd.to_numeric(df["P/B Ratio"],  errors="coerce").mean()

        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_ev_ebitda:.1f}x</div><div class="metric-label">AVG EV / EBITDA</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_ev_rev:.2f}x</div><div class="metric-label">AVG EV / REVENUE</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_pe:.1f}x</div><div class="metric-label">AVG P / E</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{avg_pb:.2f}x</div><div class="metric-label">AVG P / B</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### COMPS TABLE")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_dl, col_blank = st.columns([1, 3])
        with col_dl:
            st.download_button("⬇ DOWNLOAD CSV", df.to_csv(index=False), "comps_output.csv", "text/csv")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("### EV / EBITDA BY COMPANY")
        chart_data = df[["Ticker", "EV/EBITDA"]].copy()
        chart_data["EV/EBITDA"] = pd.to_numeric(chart_data["EV/EBITDA"], errors="coerce")
        chart_data = chart_data.dropna().set_index("Ticker")
        st.bar_chart(chart_data, color="#c9a84c")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown("### EV / REVENUE BY COMPANY")
        chart_data2 = df[["Ticker", "EV/Revenue"]].copy()
        chart_data2["EV/Revenue"] = pd.to_numeric(chart_data2["EV/Revenue"], errors="coerce")
        chart_data2 = chart_data2.dropna().set_index("Ticker")
        st.bar_chart(chart_data2, color="#c9a84c")

    else:
        st.error("No data returned. Check your API key in the .env file.")