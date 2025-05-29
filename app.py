import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

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
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    df = df.dropna(subset=['Value'])
    df['MonthYear'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    return df

def color_for_value(attr, val):
    thresholds = THRESHOLDS.get(attr)
    if thresholds is None or val is None:
        return 'gray'

    green = thresholds['green']
    yellow = thresholds['yellow']
    red = thresholds['red']

    if green < yellow < red:
        if val <= green:
            return 'green'
        elif val <= yellow:
            return 'yellow'
        else:
            return 'red'
    else:
        if val >= green:
            return 'green'
        elif val >= yellow:
            return 'yellow'
        else:
            return 'red'

def create_heatmap(df, max_rows=30):
    median_df = df.groupby(['MonthYear', 'Attribute'])['Value'].median().reset_index()
    pivot_df = median_df.pivot(index='MonthYear', columns='Attribute', values='Value')

    # Limit rows for scroll effect - keep only most recent max_rows
    if len(pivot_df) > max_rows:
        pivot_df = pivot_df.tail(max_rows)

    colors = []
    for dt in pivot_df.index:
        row_colors = []
        for attr in pivot_df.columns:
            val = pivot_df.at[dt, attr]
            color = color_for_value(attr, val)
            row_colors.append(color)
        colors.append(row_colors)

    hover_text = []
    for dt in pivot_df.index:
        row_hover = []
        dt_str = dt.strftime("%b %Y")
        for attr in pivot_df.columns:
            val = pivot_df.at[dt, attr]
            val_str = f"{val:.3f}" if pd.notnull(val) else "N/A"
            text = f"<b>{attr}</b><br>{dt_str}<br>Median: {val_str}"
            row_hover.append(text)
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
        xgap=3,
        ygap=3,
    ))

    # Add median text inside each cell
    annotations = []
    for y_i, dt in enumerate(pivot_df.index):
        for x_i, attr in enumerate(pivot_df.columns):
            val = pivot_df.at[dt, attr]
            if pd.notnull(val):
                val_str = f"{val:.2f}"
            else:
                val_str = ""
            annotations.append(
                dict(
                    x=attr,
                    y=dt.strftime("%b %Y"),
                    text=val_str,
                    showarrow=False,
                    font=dict(color="black", size=10),
                    xanchor="center",
                    yanchor="middle"
                )
            )

    fig.update_layout(
        xaxis=dict(side='top'),
        yaxis=dict(autorange='reversed'),
        template='plotly_dark',
        margin=dict(l=150, r=20, t=120, b=100),
        height=750,
        annotations=annotations,
    )

    return fig

def main():
    st.set_page_config(page_title="Economic Recession Indicator Heatmap", layout="wide", page_icon="📊")
    st.title("Economic Recession Indicator Heatmap")

    df = load_data()

    # Wrap plotly chart with a fixed height container and scroll for y-axis limitation
    st.markdown(
        """
        <style>
        .scrollable-plotly {
            max-height: 800px;
            overflow-y: auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    with st.container():
        st.markdown('<div class="scrollable-plotly">', unsafe_allow_html=True)
        fig = create_heatmap(df, max_rows=30)  # Limit to last 30 months, scroll handles rest
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
