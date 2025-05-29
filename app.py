import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -------------------
# Attribute Thresholds
# -------------------
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

DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQSg0j0ZpwXjDgSS1IEA4MA2-SwTbAhNgy8hqQVveM4eeWWIg6zxgMq-NpUIZBzQvssY2LsSo3kfc8x/pub?gid=995887444&single=true&output=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    df = df.dropna(subset=['Value'])
    df['MonthYear'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    return df

def color_for_value(attr, val):
    if pd.isna(val):
        return 'gray'
    thresholds = THRESHOLDS.get(attr)
    if not thresholds:
        return 'gray'
    green = thresholds['green']
    yellow = thresholds['yellow']
    if val <= green:
        return 'green'
    elif val <= yellow:
        return 'yellow'
    else:
        return 'red'

def create_heatmap(df):
    median_df = df.groupby(['MonthYear', 'Attribute'])['Value'].median().reset_index()
    pivot_df = median_df.pivot(index='MonthYear', columns='Attribute', values='Value')
    pivot_df = pivot_df.sort_index(ascending=False)

    colors = []
    for dt in pivot_df.index:
        row_colors = []
        for attr in pivot_df.columns:
            val = pivot_df.at[dt, attr]
            row_colors.append(color_for_value(attr, val))
        colors.append(row_colors)

    hover_text = []
    for dt in pivot_df.index:
        row_hover = []
        dt_str = dt.strftime("%b %Y")
        for attr in pivot_df.columns:
            val = pivot_df.at[dt, attr]
            val_str = f"{val:.3f}" if pd.notnull(val) else "N/A"
            row_hover.append(f"<b>{attr}</b><br>{dt_str}<br>Median: {val_str}")
        hover_text.append(row_hover)

    color_map = {'green': 0, 'yellow': 0.5, 'red': 1, 'gray': 0.25}
    z_colors = np.array([[color_map.get(c, 0.25) for c in row] for row in colors])

    fig = go.Figure(data=go.Heatmap(
        z=z_colors,
        x=pivot_df.columns,
        y=[dt.strftime("%b %Y") for dt in pivot_df.index],
        text=hover_text,
        hoverinfo='text',
        colorscale=[[0, 'green'], [0.5, 'yellow'], [1, 'red']],
        showscale=False,
        xgap=2,
        ygap=2,
    ))

    annotations = []
    for y_i, dt in enumerate(pivot_df.index):
        for x_i, attr in enumerate(pivot_df.columns):
            val = pivot_df.at[dt, attr]
            val_str = f"{val:.2f}" if pd.notnull(val) else ""
            annotations.append(dict(
                x=attr,
                y=dt.strftime("%b %Y"),
                text=val_str,
                showarrow=False,
                font=dict(color="black", size=10),
                xanchor="center",
                yanchor="middle"
            ))

    fig.update_layout(
        xaxis=dict(side='top'),
        yaxis=dict(autorange='reversed'),
        template='plotly_white',
        margin=dict(l=150, r=20, t=100, b=40),
        height=1500,  # taller chart
        annotations=annotations,
    )

    return fig, pivot_df.index.strftime("%b %Y").tolist()

def main():
    st.set_page_config(page_title="Economic Heatmap", layout="wide")
    st.title("📊 Economic Recession Indicator Heatmap")

    df = load_data()
    all_dates = sorted(df['MonthYear'].dt.strftime("%b %Y").unique(), reverse=True)

    # Date filter
    selected_dates = st.multiselect(
        "Select Months to Display (optional):",
        options=all_dates,
        default=all_dates[:36]  # show 3 years by default
    )

    if selected_dates:
        date_periods = pd.to_datetime(selected_dates).to_period("M").to_timestamp()
        df = df[df['MonthYear'].isin(date_periods)]

    fig, available_dates = create_heatmap(df)

    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
