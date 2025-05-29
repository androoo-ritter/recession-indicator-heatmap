import streamlit as st
import pandas as pd
import plotly.express as px

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQSg0j0ZpwXjDgSS1IEA4MA2-SwTbAhNgy8hqQVveM4eeWWIg6zxgMq-NpUIZBzQvssY2LsSo3kfc8x/pub?gid=995887444&single=true&output=csv"

# Thresholds for coloring each attribute (red = high concern, yellow = medium, green = good)
THRESHOLDS = {
    "3-Month": {"red": 0.5, "yellow": 1.5},
    "20-Year": {"red": 1.0, "yellow": 2.5},
    "30-Year": {"red": 1.0, "yellow": 2.5},
    "Bank Credit": {"red": -2, "yellow": -1},
    "Claims": {"red": 0.5, "yellow": 0.2},
    "Consumer Sentiment": {"red": -5, "yellow": -2},
    "Continued Claims": {"red": 0.5, "yellow": 0.2},
    "Core CPI": {"red": 3, "yellow": 2},
    "CPI": {"red": 3, "yellow": 2},
    "Credit Card Delinquency": {"red": 5, "yellow": 3},
    "Employment": {"red": -0.5, "yellow": -0.2},
    "Loans and Leases": {"red": -1.5, "yellow": -0.5},
    "M1": {"red": -5, "yellow": -2},
    "M2": {"red": -5, "yellow": -2},
    "Mortgage Delinquency": {"red": 5, "yellow": 3},
    "Payrolls": {"red": -0.5, "yellow": -0.2},
    "Real FFR": {"red": 1, "yellow": 0.5},
    "Real GDP": {"red": -1, "yellow": -0.5},
    "Retail Sales": {"red": -1, "yellow": -0.5},
    "Sahm": {"red": 0.5, "yellow": 0.3},
    "S&P500": {"red": -5, "yellow": -2},
    "Transport Jobs": {"red": -0.5, "yellow": -0.2},
    "Unemployment": {"red": 1, "yellow": 0.5},
    "USHY": {"red": 5, "yellow": 3},
    "USIG": {"red": 5, "yellow": 3},
    "VIX": {"red": 15, "yellow": 10},
}

@st.cache_data
def load_data():
    # Skip the problematic second row, parse dates, and clean data
    df = pd.read_csv(CSV_URL, skiprows=[1], parse_dates=['Date'])

    # Clean date column, drop rows with invalid dates
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])

    # Convert 'Value' to numeric, drop rows with invalid numbers
    df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
    df = df.dropna(subset=['Value'])

    # Extract Month-Year for grouping
    df['MonthYear'] = df['Date'].dt.to_period('M').dt.to_timestamp()

    return df

def create_heatmap(df):
    # Group median values by MonthYear and Attribute
    median_df = df.groupby(['MonthYear', 'Attribute'])['Value'].median().reset_index()

    # Pivot table so Attributes are rows and MonthYear are columns
    pivot = median_df.pivot(index='Attribute', columns='MonthYear', values='Value')

    # Prepare colors and tooltips
    z_colors = []
    hover_texts = []

    for attr in pivot.index:
        row_colors = []
        row_tooltips = []
        thresholds = THRESHOLDS.get(attr, {"red": 1, "yellow": 0.5})
        red_th = thresholds["red"]
        yellow_th = thresholds["yellow"]

        for val in pivot.loc[attr]:
            if pd.isna(val):
                row_colors.append("lightgrey")
                row_tooltips.append(f"{attr}: No data")
            else:
                # Assign colors based on thresholds
                if val >= red_th:
                    row_colors.append("rgb(255,0,0)")  # red
                elif val >= yellow_th:
                    row_colors.append("rgb(255,255,0)")  # yellow
                else:
                    row_colors.append("rgb(0,255,0)")  # green
                row_tooltips.append(f"{attr}: {val:.2f}")

        z_colors.append(row_colors)
        hover_texts.append(row_tooltips)

    # Create heatmap figure
    fig = px.imshow(
        pivot,
        labels=dict(x="MonthYear", y="Attribute", color="Value"),
        x=[str(d.date()) for d in pivot.columns],
        y=pivot.index,
        color_continuous_scale=["green", "yellow", "red"],
        aspect="auto",
        text_auto=False,
    )

    # Override default hovertext and colors with custom ones
    fig.data[0].hovertemplate = "%{customdata}"
    fig.data[0].customdata = hover_texts
    fig.data[0].z = z_colors  # override cell colors with our custom RGB colors

    # Enable dark mode layout
    fig.update_layout(template="plotly_dark", hovermode='closest')

    return fig

def main():
    st.set_page_config(page_title="Economic Recession Indicator Heatmap", layout="wide")
    st.title("Economic Recession Indicator Heatmap")
    st.markdown("Visualizing 26 economic indicators with color-coded thresholds based on latest data from FRED via Google Sheets.")

    df = load_data()
    fig = create_heatmap(df)
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
