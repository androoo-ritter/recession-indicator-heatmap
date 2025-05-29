import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# URL to your published Google Sheets CSV
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQSg0j0ZpwXjDgSS1IEA4MA2-SwTbAhNgy8hqQVveM4eeWWIg6zxgMq-NpUIZBzQvssY2LsSo3kfc8x/pub?gid=995887444&single=true&output=csv"

# Thresholds for each attribute to assign colors
THRESHOLDS = {
    "3-Month": {"red": -0.5, "yellow": 0.0},
    "20-Year": {"red": -0.5, "yellow": 0.0},
    "30-Year": {"red": -0.5, "yellow": 0.0},
    "Bank Credit": {"red": -0.5, "yellow": 0.0},
    "Claims": {"red": 0.5, "yellow": 0.0},
    "Consumer Sentiment": {"red": -5, "yellow": 0},
    "Continued Claims": {"red": 0.5, "yellow": 0.0},
    "Core CPI": {"red": -0.1, "yellow": 0.1},
    "CPI": {"red": -0.1, "yellow": 0.1},
    "Credit Card Delinquency": {"red": 0.5, "yellow": 0.0},
    "Employment": {"red": -0.5, "yellow": 0.0},
    "Loans and Leases": {"red": -0.5, "yellow": 0.0},
    "M1": {"red": -0.5, "yellow": 0.0},
    "M2": {"red": -0.5, "yellow": 0.0},
    "Mortgage Delinquency": {"red": 0.5, "yellow": 0.0},
    "Payrolls": {"red": -0.5, "yellow": 0.0},
    "Real FFR": {"red": 0.5, "yellow": 0.0},
    "Real GDP": {"red": -1, "yellow": 0},
    "Retail Sales": {"red": -0.5, "yellow": 0.0},
    "Sahm": {"red": 0.5, "yellow": 0.0},
    "S&P500": {"red": -0.5, "yellow": 0.0},
    "Transport Jobs": {"red": -0.5, "yellow": 0.0},
    "Unemployment": {"red": 0.5, "yellow": 0.0},
    "USHY": {"red": 0.5, "yellow": 0.0},
    "USIG": {"red": 0.5, "yellow": 0.0},
    "VIX": {"red": 0.5, "yellow": 0.0},
}

# Function to map value to color based on thresholds
def get_color(attr, val):
    thresh = THRESHOLDS.get(attr, {"red": 0, "yellow": 0})
    if val <= thresh["red"]:
        return "red"
    elif val <= thresh["yellow"]:
        return "yellow"
    else:
        return "green"

@st.cache_data
def load_data():
    # Skip the second row which contains bad headers, parse dates
    df = pd.read_csv(CSV_URL, skiprows=[1], parse_dates=['Date'])
    # Coerce bad date formats to NaT and drop those rows
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df = df.dropna(subset=['Date'])
    df['MonthYear'] = df['Date'].dt.to_period('M').dt.to_timestamp()
    return df

def create_heatmap(df):
    # Calculate median values for each MonthYear x Attribute
    median_df = df.groupby(['MonthYear', 'Attribute'])['Value'].median().reset_index()

    # Create pivot table with MonthYear rows and Attribute columns
    pivot_df = median_df.pivot(index='MonthYear', columns='Attribute', values='Value')

    # Generate color matrix based on thresholds
    color_matrix = pivot_df.copy()
    for col in color_matrix.columns:
        color_matrix[col] = color_matrix[col].apply(lambda x: get_color(col, x) if pd.notnull(x) else "gray")

    # Flatten the pivot_df for Plotly heatmap
    x_labels = list(pivot_df.columns)
    y_labels = [d.strftime("%b %Y") for d in pivot_df.index]

    # Create a list of values and corresponding colors for each cell
    z_values = pivot_df.values.tolist()
    z_colors = color_matrix.values.tolist()

    # Map color names to hex codes for Plotly
    color_map = {"red": "#e63946", "yellow": "#f1fa8c", "green": "#a8d5ba", "gray": "#d3d3d3"}

    # Create z colors as hex strings
    z_color_hex = [[color_map.get(c, "#d3d3d3") for c in row] for row in z_colors]

    # Create text annotations for hover and display
    text = []
    for i, y_val in enumerate(y_labels):
        text_row = []
        for j, x_val in enumerate(x_labels):
            val = z_values[i][j]
            if pd.isna(val):
                text_row.append(f"{x_val}<br>{y_val}<br>No Data")
            else:
                text_row.append(f"{x_val}<br>{y_val}<br>Median: {val:.2f}")
        text.append(text_row)

    # Create Plotly heatmap with annotations
    fig = px.imshow(
        z_color_hex,
        x=x_labels,
        y=y_labels,
        color_continuous_scale=None,
        aspect="auto",
        text=[[f"{v:.2f}" if pd.notnull(v) else "" for v in row] for row in z_values],
        labels=dict(x="Attribute", y="Month/Year", color="Color"),
    )

    # Update layout for dark theme and no color scale bar
    fig.update_layout(
        template="plotly_dark",
        coloraxis_showscale=False,
        xaxis=dict(side="top", tickangle=45),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=120, r=50, t=120, b=100),
        font=dict(size=10),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
    )

    # Manually set the color of each cell by updating the heatmap's colorscale and z values
    # But px.imshow doesn't support cell-level colors, so workaround:
    # We'll create a heatmap with actual values and overlay the color via z

    # Instead of px.imshow for colors, create a heatmap with original median values and use custom colorscale

    # Create colorscale array based on color matrix for each cell
    colorscale = []
    for row in z_colors:
        row_colors = []
        for c in row:
            if c == "red":
                row_colors.append(0)
            elif c == "yellow":
                row_colors.append(0.5)
            elif c == "green":
                row_colors.append(1)
            else:
                row_colors.append(np.nan)  # Gray or no data
        colorscale.append(row_colors)

    # Instead, let's create a discrete color mapping heatmap with plotly.graph_objects for better control

    import plotly.graph_objects as go

    # Prepare colors for each cell
    colors = z_color_hex

    fig = go.Figure(data=go.Heatmap(
        z=z_values,
        x=x_labels,
        y=y_labels,
        text=text,
        hoverinfo='text',
        colorscale=[[0, "#e63946"], [0.5, "#f1fa8c"], [1, "#a8d5ba"]],
        zmin=min([v for sublist in z_values for v in sublist if pd.notnull(v)]),
        zmax=max([v for sublist in z_values for v in sublist if pd.notnull(v)]),
        showscale=False,
    ))

    # Add text annotations (median values) on each cell
    annotations = []
    for i, y_val in enumerate(y_labels):
        for j, x_val in enumerate(x_labels):
            val = z_values[i][j]
            color = z_color_hex[i][j]
            if pd.notnull(val):
                annotations.append(
                    dict(
                        x=x_val,
                        y=y_val,
                        text=f"{val:.2f}",
                        showarrow=False,
                        font=dict(color='black' if color in ["#f1fa8c", "#a8d5ba"] else "white", size=9),
                        xanchor='center',
                        yanchor='middle'
                    )
                )

    fig.update_layout(
        annotations=annotations,
        template="plotly_dark",
        xaxis=dict(side="top", tickangle=45),
        yaxis=dict(autorange="reversed"),
        margin=dict(l=120, r=50, t=120, b=100),
        font=dict(size=10),
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial")
    )

    return fig

def main():
    st.set_page_config(page_title="Recession Indicator Heatmap", layout="wide", initial_sidebar_state="expanded")

    st.title("Recession Indicator Heatmap")

    df = load_data()

    st.markdown("""
    This heatmap visualizes median monthly values of economic attributes.
    Colors indicate economic stress levels:
    - **Red**: High stress/risk
    - **Yellow**: Moderate risk
    - **Green**: Low risk/stable
    """)

    fig = create_heatmap(df)

    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
