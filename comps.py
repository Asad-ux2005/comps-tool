import os
import requests
import pandas as pd
from dotenv import load_dotenv
import time

load_dotenv()
API_KEY = os.getenv("API_KEY")
BASE = "https://www.alphavantage.co/query"

TICKERS = ["WMT", "COST", "TGT", "KR", "SFM"]

def get_overview(ticker):
    r = requests.get(BASE, params={"function": "OVERVIEW", "symbol": ticker, "apikey": API_KEY})
    return r.json()

def get_income(ticker):
    r = requests.get(BASE, params={"function": "INCOME_STATEMENT", "symbol": ticker, "apikey": API_KEY})
    data = r.json()
    reports = data.get("annualReports", [])
    return reports[0] if reports else {}

def get_balance(ticker):
    r = requests.get(BASE, params={"function": "BALANCE_SHEET", "symbol": ticker, "apikey": API_KEY})
    data = r.json()
    reports = data.get("annualReports", [])
    return reports[0] if reports else {}

def safe_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0

def build_comps():
    rows = []

    for ticker in TICKERS:
        print(f"Fetching {ticker}...")

        overview = get_overview(ticker)
        time.sleep(12)

        income = get_income(ticker)
        time.sleep(12)

        balance = get_balance(ticker)
        time.sleep(12)

        if not overview or "Symbol" not in overview:
            print(f"  Skipping {ticker} - no data")
            continue

        market_cap   = safe_float(overview.get("MarketCapitalization", 0))
        total_debt   = safe_float(balance.get("shortLongTermDebtTotal", 0))
        cash         = safe_float(balance.get("cashAndCashEquivalentsAtCarryingValue", 0))
        ev           = market_cap + total_debt - cash
        revenue      = safe_float(income.get("totalRevenue", 0))
        ebitda       = safe_float(income.get("ebitda", 0))
        net_income   = safe_float(income.get("netIncome", 0))
        pe_ratio     = safe_float(overview.get("PERatio", 0))
        pb_ratio     = safe_float(overview.get("PriceToBookRatio", 0))

        rows.append({
            "Ticker":          ticker,
            "Market Cap ($m)": round(market_cap / 1e6, 1),
            "EV ($m)":         round(ev / 1e6, 1),
            "Revenue ($m)":    round(revenue / 1e6, 1),
            "EBITDA ($m)":     round(ebitda / 1e6, 1),
            "EV/Revenue":      round(ev / revenue, 2) if revenue else "N/A",
            "EV/EBITDA":       round(ev / ebitda, 2) if ebitda else "N/A",
            "P/E Ratio":       pe_ratio if pe_ratio else "N/A",
            "P/B Ratio":       pb_ratio if pb_ratio else "N/A",
            "Net Income ($m)": round(net_income / 1e6, 1),
        })

    df = pd.DataFrame(rows)

    print("\n========== COMPS TABLE ==========")
    print(df.to_string(index=False))

    df.to_excel("comps_output.xlsx", index=False)
    print("\nSaved to comps_output.xlsx")

if __name__ == "__main__":
    build_comps()
