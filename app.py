import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Google Sheets CSV URL (public, export format)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQSg0j0ZpwXjDgSS1IEA4MA2-SwTbAhNgy8hqQVveM4eeWWIg6zxgMq-NpUIZBzQvssY2LsSo3kfc8x/pub?gid=995887444&single=true&output=csv"

# Set page config and dark mode theme
st.set_page_config(page_title="Economic Indicator Heatmap", layout="wide")
st.markdown(
    """
    <style>
    body { background-color: #121212; color: white; }
    .stMarkdown, .css-1d391kg, .css-ffhzg2, .css-2trqyj { color: white; }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(CSV_URL, parse_dates=['Date'])
    # Extract Year-Month for aggregation (format like 2025-05)
    df['YearMonth'] = df['Date'].dt.to_period('M').astype(str)
    return df

df = load_data()

# List of attributes for thresholding
attributes = [
    "3-Month", "20-Year", "30-Year", "Bank Credit", "Claims", "Consumer Sentiment",
    "Continued Claims", "Core CPI", "CPI", "Credit Card Delinquency", "Employment",
    "Loans and Leases", "M1", "M2", "Mortgage Delinquency", "Payrolls", "Real FFR",
    "Real GDP", "Retail Sales", "Sahm", "S&P500", "Transport Jobs", "Unemployment",
    "USHY", "USIG", "VIX"
]

# Define color thresholds per attribute
# (example thresholds, adjust as you see fit)
thresholds = {
    "3-Month": {"red": 0.5, "yellow": 1.5},
    "20-Year": {"red": 1.5, "yellow": 2.5},
    "30-Year": {"red": 1.5, "yellow": 2.5},
    "Bank Credit": {"red": -2, "yellow": 2},
    "Claims": {"red": 300000, "yellow": 250000},
    "Consumer Sentiment": {"red": 80, "yellow": 90},
    "Continued Claims": {"red": 2000000, "yellow": 1500000},
    "Core CPI": {"red": 2.0, "yellow": 3.0},
    "CPI": {"red": 2.0, "yellow": 3.0},
    "Credit Card Delinquency": {"red": 5, "yellow": 3},
    "Employment": {"red": -100000, "yellow": 0},
    "Loans and Leases": {"red": -1.5, "yellow": 0},
    "M1": {"red": -1.0, "yellow": 1.0},
    "M2": {"red": -1.0, "yellow": 1.0},
    "Mortgage Delinquency": {"red": 3, "yellow": 2},
    "Payrolls": {"red": -200000, "yellow": 0},
    "Real FFR": {"red": 0, "yellow": 1},
    "Real GDP": {"red": -1,

