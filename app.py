import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Thresholds
THRESHOLDS = {
    '3-Month': {'green': 1.5, 'yellow': 3},
    '20-Year': {'green': 2, 'yellow': 4},
    '30-Year': {'green': 2, 'yellow': 4},
    'Bank Credit': {'green': 0, 'yellow': -2},
    'Claims': {'green': 200000, 'yellow': 300000},
    'Consumer Sentiment': {'green': 70, 'yellow': 50},
    'Continued Claims': {'green': 1500000, 'yellow': 2500000},
    'Core CPI': {'green': 2, 'yellow': 4},
    'CPI': {'green': 2, 'yellow': 4},
    'Credit Card Delinquency': {'green': 2, 'yellow': 4},
    'Employment': {'green': 100000, 'yellow': 0},
    'Loans and Leases': {'green': 0, 'yellow': -2},
    'M1': {'green': 0, 'yellow': -2},
    'M2': {'green': 0, 'yellow': -2},
    'Mortgage Delinquency': {'green': 2, 'yellow': 4},
    'Payrolls': {'green': 0, 'yellow': -100000},
    'Real FFR': {'green': 0, 'yellow': 1},
    'Real GDP': {'green': 0, 'yellow': -1},
    'Retail Sales': {'green': 0, 'yellow': -1},
    'Sahm': {'green': 0.5, 'yellow': 0.8},
    'S&P500': {'green': 0, 'yellow': -5},
    'Transport Jobs': {'green': 0, 'yellow': -20000},
    'Unemployment': {'green': 4, 'yellow': 6},
    'USHY': {'green': 4, 'yellow': 6},
    'USIG': {'green': 2, 'yellow': 4},
    'VIX': {'green': 20, 'yellow': 30},
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
    if attr not in THRESHOLDS or pd.isnull(val):
        return "lightgrey"
    t = THRESHOLDS[attr]
    if val <= t["green"]:
        return "green"
    elif val <= t["yellow"]:
        return "yellow"
    else:
        return "red"

def create_heatmap(df):
    median_df = df.groupby(["MonthYear", "Attribute"])["Value"].median().reset_index()
    pivot_df = median_df.pivot(index="MonthYear", columns="Attribute", values="Value").sort_index(ascending=False)

    z_text = pivot_df.round(2).astype(str)
    colors = [[color_for_value(col, pivot_df.loc[row_idx, col]) for col in pivot_df.columns] for row_idx in pivot_df.index]

    fig = go.Figure(data=go.Heatmap(
        z=[[1]*len(pivot_df.columns)]*len(pivot_df.index),
        x=pivot_df.columns,
        y=pivot_df.index.strftime("%b %Y"),
        text=z_text,
        hovertext=[
            [f"{col}<br>{idx.strftime('%b %Y')}<br>{pivot_df.loc[idx, col]:.2f}" if not pd.isnull(pivot_df.loc[idx, col]) else "No Data"
             for col in pivot_df.columns] for idx in pivot_df.index
        ],
        hoverinfo="text",
        showscale=False,
        texttemplate="%{text}",
        textfont={"size":12},
        xgap=2,
        ygap=2,
        colorscale=[[0, "white"], [1, "white"]],
        zmin=0,
        zmax=1,
    ))

    for i, row in enumerate(colors):
        for j, c in enumerate(row):
            fig.add_shape(
                type="rect",
                x0=j-0.5, y0=i-0.5,
                x1=j+0.5, y1=i+0.5,
                fillcolor=c, line=dict(width=0)
            )

    fig.update_layout(height=900, margin=dict(t=30, b=30))
    return fig

def main():
    st.set_page_config(page_title="Economic Recession Indicator", layout="wide")
    st.title("📊 Economic Recession Indicator Heatmap")

    with st.expander("ℹ️ Disclaimer"):
        st.markdown("""
        > **Disclaimer**  
        > This dashboard uses publicly available economic time series data from the [Federal Reserve Economic Data (FRED)](https://fred.stlouisfed.org/) database.  
        > It is intended for **educational purposes only** and **should not be interpreted as financial or investment advice**.  
        > Please independently verify any figures you use from this page.  
        >  
        > Given that each economic indicator is published at different intervals (daily, monthly, quarterly, etc.),  
        > this tool aggregates data by computing the **median value for each indicator per month**.
        """)

    with st.expander("🎨 Color Legend"):
        st.markdown("""
        - 🟩 **Green**: Healthy/expected range  
        - 🟨 **Yellow**: Caution  
        - 🟥 **Red**: Warning / likely signal  
        - ⬜ **Grey**: No data available for that month
        """)

    df = load_data()
    fig = create_heatmap(df)
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
