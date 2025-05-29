import streamlit as st
import pandas as pd
import plotly.graph_objects as go

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQSg0j0ZpwXjDgSS1IEA4MA2-SwTbAhNgy8hqQVveM4eeWWIg6zxgMq-NpUIZBzQvssY2LsSo3kfc8x/pub?gid=995887444&single=true&output=csv"

THRESHOLDS = {
    "CPI": {"red": 0.5, "yellow": 0.2},
    "Unemployment": {"red": 7, "yellow": 5},
    # Add all attribute thresholds as needed
}

def get_color(value, attr):
    thresh = THRESHOLDS.get(attr, {})
    red = thresh.get("red", None)
    yellow = thresh.get("yellow", None)

    if red is None or yellow is None:
        return "lightgray"  # Default color

    if value >= red:
        return "red"
    elif value >= yellow:
        return "yellow"
    else:
        return "green"


@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(CSV_URL)

    # Drop the 2nd row if it is a duplicate header row
    if (df.iloc[0] == df.columns).all():
        df = df.iloc[1:]

    # Convert 'Date' column to datetime, drop errors
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    # Convert 'Value' to numeric, coercing errors to NaN
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

    # Drop rows with NaN in 'Value' or 'Attribute'
    df = df.dropna(subset=["Value", "Attribute"])

    # Add MonthYear for grouping
    df["MonthYear"] = df["Date"].dt.to_period("M").dt.to_timestamp()

    return df

def create_heatmap(df):
    median_df = df.groupby(["MonthYear", "Attribute"])["Value"].median().reset_index()

    pivot_df = median_df.pivot(index="MonthYear", columns="Attribute", values="Value")

    hover_text = pivot_df.applymap(lambda v: f"{v:.2f}" if pd.notnull(v) else "No data")

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=[d.strftime("%Y-%m") for d in pivot_df.index],
            text=hover_text.values,
            hoverinfo="text",
            colorscale=[[0, "green"], [0.5, "yellow"], [1, "red"]],
            showscale=True,
            zmin=pivot_df.min().min(),
            zmax=pivot_df.max().max(),
        )
    )

    fig.update_layout(
        title="Economic Indicators Heatmap",
        xaxis_title="Indicator",
        yaxis_title="Month-Year",
        template="plotly_dark",
        height=600,
    )

    return fig

def main():
    st.set_page_config(page_title="Economic Heatmap", layout="wide", initial_sidebar_state="auto")
    st.title("Economic Indicator Recession Heatmap")

    df = load_data()

    st.write("Data preview:")
    st.write(df.head(10))

    if df.empty:
        st.error("No data available to display.")
        return

    fig = create_heatmap(df)
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
