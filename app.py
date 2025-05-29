import pandas as pd
import streamlit as st
import plotly.express as px

# URL of the published Google Sheet as CSV
CSV_URL = 'https://docs.google.com/spreadsheets/d/1gWPHkN2cKFf-i0xELlLRJp7xrhMCmqmkBFPglX8-u4M/gviz/tq?tqx=out:csv&gid=995887444'

# Load data
df = pd.read_csv(CSV_URL, parse_dates=['Date'])

# Preprocess
df['Month'] = df['Date'].dt.to_period('M').astype(str)

# Define thresholds (example)
thresholds = {
    '3-Month': (2, 5),
    '20-Year': (3, 6),
    '30-Year': (3, 6),
    'Bank Credit': (16000, 17000),
    'Claims': (200, 400),
    'Consumer Sentiment': (60, 85),
    'Continued Claims': (1200, 1800),
    'Core CPI': (2, 4),
    'CPI': (2, 4),
    'Credit Card Delinquency': (2, 4),
    'Employment': (150000, 300000),
    'Loans and Leases': (16000, 17000),
    'M1': (18000, 20000),
    'M2': (20000, 22000),
    'Mortgage Delinquency': (2, 5),
    'Payrolls': (150000, 300000),
    'Real FFR': (0, 2.5),
    'Real GDP': (1, 3),
    'Retail Sales': (600000, 700000),
    'Sahm': (0.5, 0.8),
    'S&P500': (3500, 5000),
    'Transport Jobs': (500, 800),
    'Unemployment': (3, 5),
    'USHY': (6, 9),
    'USIG': (3, 5),
    'VIX': (15, 25),
}

# Compute medians
median_df = df.groupby(['Month', 'Attribute'])['Value'].median().reset_index()
pivot_df = median_df.pivot(index='Month', columns='Attribute', values='Value').sort_index()

# Assign color categories
def get_color(value, attr):
    if attr not in thresholds or pd.isna(value):
        return 'gray'
    low, high = thresholds[attr]
    if value < low:
        return 'green'
    elif value < high:
        return 'yellow'
    else:
        return 'red'

color_df = pivot_df.copy()
for col in color_df.columns:
    color_df[col] = pivot_df[col].apply(lambda x: get_color(x, col))

# Build Streamlit app
st.title("Economic Heatmap Dashboard")
st.markdown("_Based on median monthly values. Not financial advice. Data from FRED._")

# Render heatmap table with colors
def color_cells(val, color):
    return f'background-color: {color}; color: black; font-weight: bold'

styled_df = pivot_df.style.apply(lambda col: [color_cells(v, get_color(v, col.name)) for v in col], axis=0)\
                          .format("{:.2f}")

st.dataframe(styled_df, use_container_width=True)
