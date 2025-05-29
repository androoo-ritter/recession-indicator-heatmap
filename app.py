import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# CSV data URL
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQSg0j0ZpwXjDgSS1IEA4MA2-SwTbAhNgy8hqQVveM4eeWWIg6zxgMq-NpUIZBzQvssY2LsSo3kfc8x/pub?gid=995887444&single=true&output=csv"

# Define thresholds (example for a few attributes, expand as needed)
THRESHOLDS = {
    "CPI": {"red": 0.5, "yellow": 0.2},
    "Unemployment": {"red": 7, "yellow": 5},
    # Add all 26 attribute thresholds here ...
}

# Color map
def get_color(value, attr):
    thresh = THRESHOLDS.get(attr, {})
    red = thresh.get("red", None)
    yellow = thresh.get("yellow", None)

    if red is None or yellow is None:
        return "lightgray"  # Default color if no thresholds defined

    if value >= red:
        return "red"
    elif value >= yellow:
        return "yellow"
    else:
        return "green"


@st.cache_data(ttl=3600)
def load_data():
    df = pd.read_csv(CSV_URL, parse_dates=["Date"])

    # Debug output to check raw data
    st.write("Raw data preview:")
    st.write(df.head(10))

    # Remove the second row which might be the problematic header row in your CSV
    if (df.iloc[0] == df.columns).all():
        df = df.iloc[1:]

    # Convert 'Date' column to datetime if not already
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

    # Drop rows with invalid dates
    df = df.dropna(subset=["Date"])

    # Debug output to confirm after cleanup
    st.write("Data after cleaning:")
    st.write(df.head(10))

    # Add MonthYear column for aggregation
    df["MonthYear"] = df["Date"].dt.to_period("M").dt.to_timestamp()

    return df


def create_heatmap(df):
    # Median by MonthYear and Attribute
    median_df = df.groupby(["MonthYear", "Attribute"])["Value"].median().reset_index()

    # Debug output for median_df
    st.write("Median values grouped by MonthYear and Attribute:")
    st.write(median_df.head(20))

    # Pivot to get matrix for heatmap
    pivot_df = median_df.pivot(index="MonthYear", columns="Attribute", values="Value")

    # Debug pivot table
    st.write("Pivoted DataFrame for heatmap:")
    st.write(pivot_df.head())

    # Map colors based on thresholds
    colors = pivot_df.copy()
    for col in colors.columns:
        colors[col] = colors[col].apply(lambda v: get_color(v, col))

    # Create hover text
    hover_text = pivot_df.applymap(lambda v: f"{v:.2f}" if pd.notnull(v) else "No data")

    # Create heatmap figure
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

    if df.empty:
        st.error("No data available to display.")
        return

    fig = create_heatmap(df)
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
