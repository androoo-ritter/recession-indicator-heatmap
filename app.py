import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- Thresholds ---
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
    'S&P500': {'green': 0, 'yellow': -5, 'red_expl': 'Major market decline'},
    'Transport Jobs': {'green': 0, 'yellow': -20000, 'red_expl': 'Demand-side weakness'},
    'Unemployment': {'green': 4, 'yellow': 6, 'red_expl': 'Labor market deterioration'},
    'USHY': {'green': 4, 'yellow': 6, 'red_expl': 'Risk premium surging'},
    'USIG': {'green': 2, 'yellow': 4, 'red_expl': 'Credit stress in investment grade'},
    'VIX': {'green': 20, 'yellow': 30, 'red_expl': 'High market volatility'},
}

FRED_SOURCES = {
    "3-Month": "https://fred.stlouisfed.org/series/DGS3MO",
    "20-Year": "https://fred.stlouisfed.org/series/DGS20",
    "30-Year": "https://fred.stlouisfed.org/series/DGS30",
    "Bank Credit": "https://fred.stlouisfed.org/series/TOTBKCR",
    "Claims": "https://fred.stlouisfed.org/series/ICSA",
    "Consumer Sentiment": "https://fred.stlouisfed.org/series/UMCSENT",
    "Continued Claims": "https://fred.stlouisfed.org/series/CCSA",
    "Core CPI": "https://fred.stlouisfed.org/series/CPILFESL",
    "CPI": "https://fred.stlouisfed.org/series/CPIAUCSL",
    "Credit Card Delinquency": "https://fred.stlouisfed.org/series/DRCCLACBS",
    "Employment": "https://fred.stlouisfed.org/series/UNRATE",
    "Loans and Leases": "https://fred.stlouisfed.org/series/TOTLL",
    "M1": "https://fred.stlouisfed.org/series/M1SL",
    "M2": "https://fred.stlouisfed.org/series/M2SL",
    "Mortgage Delinquency": "https://fred.stlouisfed.org/series/DRSFRMACBS",
    "Payrolls": "https://fred.stlouisfed.org/series/PAYEMS",
    "Real FFR": "https://fred.stlouisfed.org/series/FEDFUNDS",
    "Real GDP": "https://fred.stlouisfed.org/series/A191RL1Q225SBEA",
    "Retail Sales": "https://fred.stlouisfed.org/series/RSXFS",
    "Sahm": "https://fred.stlouisfed.org/series/SAHMREALTIME",
    "S&P500": "https://fred.stlouisfed.org/series/SP500",
    "Transport Jobs": "https://fred.stlouisfed.org/series/CES4348400001",
    "Unemployment": "https://fred.stlouisfed.org/series/UNRATE",
    "USHY": "https://fred.stlouisfed.org/series/BAMLH0A0HYM2",
    "USIG": "https://fred.stlouisfed.org/series/BAMLC0A0CM",
    "VIX": "https://fred.stlouisfed.org/series/VIXCLS",
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
    t = THRESHOLDS.get(attr)
    if val is None or attr not in THRESHOLDS:
        return "lightgrey"
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
    colors = [[color_for_value(col, val) for col in pivot_df.columns] for val in pivot_df.values]

    fig = go.Figure(data=go.Heatmap(
        z=[[1]*len(pivot_df.columns)]*len(pivot_df.index),  # dummy z values
        x=pivot_df.columns,
        y=pivot_df.index.strftime("%b %Y"),
        text=z_text,
        hovertext=[
            [f"{col}<br>{idx.strftime('%b %Y')}<br>{pivot_df.loc[idx, col]:.2f}" if not pd.isna(pivot_df.loc[idx, col]) else "No Data"
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
        This dashboard uses publicly available economic time series data from the [Federal Reserve Economic Data (FRED)](https://fred.stlouisfed.org/) database.  
        It is intended for **educational purposes only** and **should not be interpreted as financial or investment advice**.  
        Please independently verify any figures you use from this page.  
        Data is aggregated by computing the **median value for each indicator per month**.
        """)

    with st.expander("🎨 Color Legend"):
        st.markdown("""
        - 🟩 **Green**: Healthy/expected range  
        - 🟨 **Yellow**: Caution  
        - 🟥 **Red**: Warning / likely signal  
        - ⬜ **Grey**: No data available for that month
        """)

    df = load_data()
    latest_dates = df["MonthYear"].sort_values(ascending=False).dt.strftime("%b %Y").unique()
    selected_dates = st.multiselect("Select Months to View", latest_dates, default=latest_dates[:24])

    df_filtered = df[df["MonthYear"].dt.strftime("%b %Y").isin(selected_dates)]
    fig = create_heatmap(df_filtered)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("🎯 View Thresholds by Data Point"):
        threshold_df = pd.DataFrame([
            {"Data Point": attr, "Green ≤": v["green"], "Yellow ≤": v["yellow"], "Red >": f">{v['yellow']}", "Explanation": v["red_expl"]}
            for attr, v in THRESHOLDS.items()
        ])
        st.dataframe(threshold_df, use_container_width=True)

    with st.expander("📎 View FRED Data Source Reference"):
        st.markdown("Each metric below links directly to its FRED series page.")
        st.markdown("<table><thead><tr><th>Data Point</th><th>FRED Link</th></tr></thead><tbody>" + "".join(
            f"<tr><td>{dp}</td><td><a href='{url}' target='_blank'>{url}</a></td></tr>" 
            for dp, url in FRED_SOURCES.items()) + "</tbody></table>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
