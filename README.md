# Comps Tool
 https://comps-tool-ih2zx5wjnb3dx9my7yukyz.streamlit.app/
# Automated Comparable Company Analysis Tool

A Python script that automatically pulls live financial data via the Alpha Vantage API and generates a comparable company analysis (comps) table — the core valuation tool used in investment banking.

## What it does
- Fetches live data for 5 companies automatically
- Calculates key valuation multiples: EV/EBITDA, EV/Revenue, P/E, P/B
- Outputs a clean comps table in the terminal
- Saves results to Excel (comps_output.xlsx)

## Metrics calculated
- Market Capitalisation
- Enterprise Value (Market Cap + Debt - Cash)
- EV/Revenue
- EV/EBITDA
- P/E Ratio
- P/B Ratio
- Net Income

## How to run
1. Clone the repo
2. Add your Alpha Vantage API key to a `.env` file: `API_KEY=yourkey`
3. Install dependencies: `pip install requests pandas openpyxl python-dotenv`
4. Run: `python comps.py`

## Tech used
- Python
- Alpha Vantage API
- pandas

- openpyxl
  <img width="1286" height="566" alt="image" src="https://github.com/user-attachments/assets/6924883e-5470-4cb8-9958-61158043902b" />

