import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# -- CONFIG --
st.set_page_config(page_title="Economic Indicators Heatmap", layout="wide", initial_sidebar_state="collapsed")

# Dark mode CSS
dark_style = """
<style>
body, .stApp {
    background-color: #121212;
    color: white;
}
.css-18e3th9 {
    background-color: #121212;
}
</style>
"""
st.markdown(dark_style, unsafe_allow_html=True)

# Data URL (public CSV export of your Google Sheet)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQSg0j0ZpwXjDgSS1IEA4MA2-SwTbAhNgy8hqQVveM4eeWWIg6zxgMq-NpUIZBzQvssY2LsSo3kfc8x/pub?gid=995887444&single=true&output=csv"

@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(CSV_URL, parse_dates=['Date'])
    # Format Date as month/year for row grouping
    df['MonthYear'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    return df

df = load_data()

# Define thresholds for coloring (example values, adjust as needed)
thresholds = {
    "3-Month": {"red": 0.01, "yellow": 0.02, "green": 0.03},
    "20-Year": {"red": 1.0, "yellow": 2.0, "green": 3.0},
    "30-Year": {"red": 1.5, "yellow": 2.5, "green": 3.5},
    "Bank Credit": {"red": -0.5, "yellow": 0, "green": 0.5},
    "Claims": {"red": 5, "yellow": 3, "green": 1},
    "Consumer Sentiment": {"red": 80, "yellow": 90, "green": 100},
    "Continued Claims": {"red": 10, "yellow": 7, "green": 4},
    "Core CPI": {"red": 0.01, "yellow": 0.02, "green": 0.03},
    "CPI": {"red": 0.01, "yellow": 0.02, "green": 0.03},
    "Credit Card Delinquency": {"red": 2.0, "yellow": 1.0, "green": 0.5},
    "Employment": {"red": -1000, "yellow": 0, "green": 1000},
    "Loans and Leases": {"red": -0.3, "yellow": 0, "green": 0.3},
    "M1": {"red": -1.0, "yellow": 0, "green": 1.0},
    "M2": {"red": -1.0, "yellow": 0, "green": 1.0},
    "Mortgage Delinquency": {"red": 5, "yellow": 3, "green": 1},
    "Payrolls": {"red": -1000, "yellow": 0, "green": 1000},
    "Real FFR": {"red": 1.0, "yellow": 0.5, "green": 0},
    "Real GDP": {"red": -1, "yellow": 0, "green": 1},
    "Retail Sales": {"red": -0.5, "yellow": 0, "green": 0.5},
    "Sahm": {"red": 0.1, "yellow": 0.05, "green": 0},
    "S&P500": {"red": -10, "yellow": 0, "green": 10},
    "Transport Jobs": {"red": -500, "yellow": 0, "green": 500},
    "Unemployment": {"red": 6, "yellow": 5, "green": 4},
    "USHY": {"red": 3, "yellow": 2, "green": 1},
    "USIG": {"red": 3, "yellow": 2, "green": 1},
    "VIX": {"red": 25, "yellow": 20, "green": 15}
}

# Compute median value per MonthYear and Attribute
medians = df.groupby(['MonthYear', 'Attribute'])['Value'].median().reset_index()

# Pivot to create matrix: rows=MonthYear, cols=Attribute, values=median Value
pivot_df = medians.pivot(index='MonthYear', columns='Attribute', values='Value').sort_index(ascending=False)

# Create a color matrix with same shape as pivot_df based on thresholds
def color_for_value(attr, val):
    if pd.isna(val):
        return "#222222"  # dark grey for missing
    thr = thresholds.get(attr, None)
    if not thr:
        return "#444444"  # default grey if no threshold set
    if val <= thr["red"]:
        return "#ff4c4c"  # red
    elif val <= thr["yellow"]:
        return "#ffec4c"  # yellow
    else:
        return "#4cff4c"  # green

colors = pivot_df.copy()
for col in colors.columns:
    colors[col] = colors[col].apply(lambda x: color_for_value(col, x))

# Prepare hover text matrix
hover_text = pivot_df.copy()
for idx in pivot_df.index:
    for col in pivot_df.columns:
        val = pivot_df.loc[idx, col]
        hover_text.loc[idx, col] = f"Date: {idx.strftime('%b %Y')}<br>Attribute: {col}<br>Median Value: {val if not pd.isna(val) else 'N/A'}"

# Create heatmap figure with Plotly
fig = go.Figure(data=go.Heatmap(
    z=pivot_df.values,
    x=pivot_df.columns,
    y=[d.strftime('%b %Y') for d in pivot_df.index],
    text=pivot_df.round(2).astype(str),  # Text labels with median values rounded
    hoverinfo='text',
    hovertext=hover_text.values,
    colorscale=[[0, '#ff4c4c'], [0.5, '#ffec4c'], [1, '#4cff4c']],  # dummy colorscale; actual colors set below
    showscale=False,
))

# Manually set colors per cell (Plotly trick using z and colorscale is limited, so override with colors matrix)
fig.data[0].colorscale = None
fig.data[0].z = np.arange(pivot_df.size).reshape(pivot_df.shape)  # dummy numeric matrix for proper sizing
fig.data[0].zmin = 0
fig.data[0].zmax = pivot_df.size

fig.data[0].colors = colors.values.flatten()

fig.update_traces(
    textfont={"color": "black", "size": 10},
    text=pivot_df.round(2).astype(str).values,
    hoverlabel=dict(bgcolor="white", font_size=12),
)

fig.update_layout(
    yaxis=dict(autorange='reversed'),
    plot_bgcolor='#121212',
    paper_bgcolor='#121212',
    font=dict(color='white'),
    margin=dict(l=80, r=80, t=60, b=60),
    height=900,
    width=1400,
    title="Economic Indicators Heatmap (Median values with color thresholds)",
)

st.title("📊 Economic Indicators Heatmap")

st.write("Showing median values per Month/Year and Attribute. Color indicates value vs. thresholds (green=good, yellow=caution, red=bad).")

st.plotly_chart(fig, use_container_width=True)
