import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Full thresholds for all 26 attributes
THRESHOLDS = {
    "3-Month": {"green": 0.0, "yellow": 3.0, "red": 6.0},
    "20-Year": {"green": 1.0, "yellow": 2.0, "red": 3.0},
    "30-Year": {"green": 1.0, "yellow": 2.0, "red": 3.0},
    "Bank Credit": {"green": 2.0, "yellow": 4.0, "red": 6.0},
    "Claims": {"green": 100000, "yellow": 300000, "red": 600000},
    "Consumer Sentiment": {"green": 90, "yellow": 80, "red": 70},
    "Continued Claims": {"green": 200000, "yellow": 400000, "red": 700000},
    "Core CPI": {"green": 1.0, "yellow": 2.0, "red": 3.0},
    "CPI": {"green": 0.0, "yellow": 2.0, "red": 3.0},
    "Credit Card Delinquency": {"green": 1.0, "yellow": 2.5, "red": 5.0},
    "Employment": {"green": 1000000, "yellow": 500000, "red": 0},
    "Loans and Leases": {"green": 0.0, "yellow": 3.0, "red": 6.0},
    "M1": {"green": 2.0, "yellow": 4.0, "red": 6.0},
    "M2": {"green": 2.0, "yellow": 4.0, "red": 6.0},
    "Mortgage Delinquency": {"green": 1.0, "yellow": 3.0, "red": 6.0},
    "Payrolls": {"green": 500000, "yellow": 200000, "red": 0},
    "Real FFR": {"green": 0.0, "yellow": 2.0, "red": 4.0},
    "Real GDP": {"green": 2.0, "yellow": 1.0, "red": -1.0},
    "Retail Sales": {"green": 3.0, "yellow": 1.0, "red": -2.0},
    "Sahm": {"green": 0.0, "yellow": 0.5, "red": 1.0},
    "S&P500": {"green": 0.0, "yellow": -5.0, "red": -10.0},
    "Transport Jobs": {"green": 100000, "yellow": 50000, "red": 0},
    "Unemployment": {"green": 3.0, "yellow": 5.0, "red": 7.0},
    "USHY": {"green": 2.0, "yellow": 4.0, "red": 6.0},
    "USIG": {"green": 1.5, "yellow": 3.0, "red": 5.0},
    "VIX": {"green": 10, "yellow": 20, "red": 30},
}

DATA_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQSg0j0ZpwXjDgSS1IEA4MA2-SwTbAhNgy8hqQVveM4eeWWIg6zxgMq-NpUIZBzQvssY2LsSo3kfc8x/pub?gid=995887444&single=true&output=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    # Skip the second header-like row if it exists
    if df.iloc[0].equals(pd.Series(["Date", "CPI", "CPI"])):
        df = df.iloc[1:]
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])  # Drop rows where Date conversion failed
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    df = df.dropna(subset=['Value'])
    df['MonthYear'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    return df

def color_for_value(attr, val):
    thresholds = THRESHOLDS.get(attr)
    if thresholds is None or val is None:
        return 'gray'  # fallback color

    green = thresholds['green']
    yellow = thresholds['yellow']
    red = thresholds['red']

    # Check if increasing values are bad (green < yellow < red)
    if green < yellow < red:
        if val <= green:
            return 'green'
        elif val <= yellow:
            return 'yellow'
        else:
            return 'red'
    else:
        # Decreasing values are bad (red < yellow < green)
        if val >= green:
            return 'green'
        elif val >= yellow:
            return 'yellow'
        else:
            return 'red'

def create_heatmap(df):
    # Calculate median per MonthYear + Attribute
    median_df = df.groupby(['MonthYear', 'Attribute'])['Value'].median().reset_index()

    # Pivot so rows=Attribute, columns=MonthYear
    pivot_df = median_df.pivot(index='Attribute', columns='MonthYear', values='Value')

    # Prepare colors matrix matching pivot_df shape
    colors = []
    for attr in pivot_df.index:
        row_colors = []
        for val in pivot_df.loc[attr]:
            color = color_for_value(attr, val)
            row_colors.append(color)
        colors.append(row_colors)

    # Create annotations for tooltip content: month, year, attribute, median value
    hover_text = []
    for attr in pivot_df.index:
        row_hover = []
        for dt, val in pivot_df.loc[attr].items():
            dt_str = dt.strftime("%b %Y") if pd.notnull(dt) else ""
            val_str = f"{val:.3f}" if pd.notnull(val) else "N/A"
            text = f"<b>{attr}</b><br>{dt_str}<br>Median: {val_str}"
            row_hover.append(text)
        hover_text.append(row_hover)

    fig = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=[dt.strftime("%b %Y") for dt in pivot_df.columns],
        y=pivot_df.index,
        hoverinfo='text',
        text=hover_text,
        colorscale=[[0, 'green'], [0.5, 'yellow'], [1, 'red']],  # Placeholder; colors come from custom list
        showscale=False,
        zmin=np.nanmin(pivot_df.values),
        zmax=np.nanmax(pivot_df.values),
        xgap=1,
        ygap=1,
        ))

    # Because Plotly Heatmap doesn't accept a direct color list, use colors as annotations instead
    # So instead, create colored rectangles using shapes or use a workaround by coloring cells via annotations.
    # Here we override the colorscale for simplicity; better approach is to use colored squares with annotations.

    # Remove automatic xaxis type (which can sometimes cause ticks issues)
    fig.update_layout(
        xaxis=dict(tickangle=45, side='top'),
        yaxis=dict(autorange='reversed'),  # So that first attribute is on top
        template="plotly_dark",
        margin=dict(l=120, b=100, t=100, r=20),
        height=700,
    )

    # Manually color the heatmap cells by mapping colors to z values — workaround with discrete colors
    # Plotly does not support per-cell color for heatmap directly, so using 'z' colorscale is workaround
    # We can map values to a numeric scale corresponding to colors:
    color_map = {'green': 0, 'yellow': 0.5, 'red': 1, 'gray': 0.25}
    z_colors = np.array([[color_map.get(c, 0.25) for c in row] for row in colors])
    fig.data[0].z = z_colors
    fig.data[0].colorscale = [[0, 'green'], [0.5, 'yellow'], [1, 'red']]
    fig.data[0].colorbar = None

    return fig

def main():
    st.set_page_config(page_title="Economic Recession Indicator Heatmap", layout="wide", page_icon="📊")
    st.title("Economic Recession Indicator Heatmap")

    df = load_data()

    fig = create_heatmap(df)

    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
