import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Thresholds per attribute with red zone explanation
THRESHOLDS = {
    '3-Month': {'green': 1.5, 'yellow': 3, 'red_expl': 'Excessively high short-term interest rates'},
    '20-Year': {'green': 2, 'yellow': 4, 'red_expl': 'Long-term rates may signal inflation or instability'},
    '30-Year': {'green': 2, 'yellow': 4, 'red_expl': 'Long-term borrowing costs high'},
    'Bank Credit': {'green': 0, 'yellow': -2, 'red_expl': 'Contraction in lending activity'},
    'Claims': {'green': 200000, 'yellow': 300000, 'red_expl': 'Spike in unemployment claims'},
    'Consumer Sentiment': {'green': 70, 'yellow': 50, 'red_expl': 'Low consumer confidence'},
    'Continued Claims': {'green': 1500000, 'yellow': 2500000, 'red_expl': 'Extended unemployment'},
    'Core CPI': {'green': 2, 'yellow': 4, 'red_expl': 'Elevated core inflation'},
    'CPI': {'green': 2, 'yellow': 4, 'red_expl': 'Elevated inflation'},
    'Credit Card Delinquency': {'green': 2, 'yellow': 4, 'red_expl': 'Consumers struggling with debt'},
    'Employment': {'green': 100000, 'yellow': 0, 'red_expl': 'Net job losses'},
    'Loans and Leases': {'green': 0, 'yellow': -2, 'red_expl': 'Decrease in bank lending'},
    'M1': {'green': 0, 'yellow': -2, 'red_expl': 'Shrinking money supply'},
    'M2': {'green': 0, 'yellow': -2, 'red_expl': 'Shrinking broader money supply'},
    'Mortgage Delinquency': {'green': 2, 'yellow': 4, 'red_expl': 'Housing distress'},
    'Payrolls': {'green': 0, 'yellow': -100000, 'red_expl': 'Significant job loss'},
    'Real FFR': {'green': 0, 'yellow': 1, 'red_expl': 'Restrictive monetary policy'},
    'Real GDP': {'green': 0, 'yellow': -1, 'red_expl': 'Economic contraction'},
    'Retail Sales': {'green': 0, 'yellow': -1, 'red_expl': 'Declining consumer spending'},
    'Sahm': {'green': 0.5, 'yellow': 0.8, 'red_expl': 'Likely start of a recession'},
    'SP500': {'green': 0, 'yellow': -5, 'red_expl': 'Major market decline'},  # Fixed here
    'Transport Jobs': {'green': 0, 'yellow': -20000, 'red_expl': 'Demand-side weakness'},
    'Unemployment': {'green': 4, 'yellow': 6, 'red_expl': 'Labor market deterioration'},
    'USHY': {'green': 4, 'yellow': 6, 'red_expl': 'Risk premium surging'},
    'USIG': {'green': 2, 'yellow': 4, 'red_expl': 'Credit stress in investment grade'},
    'VIX': {'green': 20, 'yellow': 30, 'red_expl': 'High market volatility'},
}

FRED_SOURCES = {
    # same as your previous code
}

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQSg0j0ZpwXjDgSS1IEA4MA2-SwTbAhNgy8hqQVveM4eeWWIg6zxgMq-NpUIZBzQvssY2LsSo3kfc8x/pub?gid=995887444&single=true&output=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    df = df.dropna(subset=['Date', 'Value'])
    df['MonthYear'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    return df

def color_for_value(attr, val):
    if pd.isna(val):
        return 'gray'
    t = THRESHOLDS.get(attr)
    if not t:
        return 'gray'
    if val <= t['green']:
        return 'green'
    elif val <= t['yellow']:
        return 'yellow'
    else:
        return 'red'

def create_heatmap(df, selected_months):
    attributes = df['Attribute'].unique()
    all_months = pd.date_range(df['MonthYear'].min(), df['MonthYear'].max(), freq='MS').to_period('M').to_timestamp()
    full_index = pd.MultiIndex.from_product([attributes, all_months], names=['Attribute', 'MonthYear'])

    median_df = df.groupby(['Attribute', 'MonthYear'])['Value'].median().round(2)
    full_df = median_df.reindex(full_index).reset_index()
    full_df = full_df[full_df['MonthYear'].isin(selected_months)]

    pivot_df = full_df.pivot(index='MonthYear', columns='Attribute', values='Value').sort_index(ascending=False)

    colors = []
    for dt in pivot_df.index:
        colors.append([color_for_value(attr, pivot_df.at[dt, attr]) for attr in pivot_df.columns])

    hover_text = []
    for dt in pivot_df.index:
        row = []
        dt_str = dt.strftime("%b %Y")
        for attr in pivot_df.columns:
            val = pivot_df.at[dt, attr]
            val_str = f"{val:.2f}" if pd.notnull(val) else "N/A"
            row.append(f"<b>{attr}</b><br>{dt_str}<br>Median: {val_str}")
        hover_text.append(row)

    color_map = {'gray': 0.0, 'green': 0.001, 'yellow': 0.5, 'red': 1.0}
    z_colors = np.array([[color_map.get(c, 0.0) for c in row] for row in colors])

    fig = go.Figure(data=go.Heatmap(
        z=z_colors,
        x=pivot_df.columns,
        y=[d.strftime("%b %Y") for d in pivot_df.index],
        text=hover_text,
        hoverinfo='text',
        colorscale=[
            [0.0, 'lightgray'],   # Grey for missing data
            [0.001, 'green'],
            [0.5, 'yellow'],
            [1.0, 'red']
        ],
        showscale=False,
        xgap=2,
        ygap=2
    ))

    annotations = []
    for y_idx, dt in enumerate(pivot_df.index):
        for x_idx, attr in enumerate(pivot_df.columns):
            val = pivot_df
