import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Thresholds dict here (omitted for brevity, just copy from prior)

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
    # Same threshold logic as before
    # ...

def create_heatmap(df, max_rows=100):
    median_df = df.groupby(['MonthYear', 'Attribute'])['Value'].median().reset_index()
    pivot_df = median_df.pivot(index='MonthYear', columns='Attribute', values='Value')

    # Sort descending (latest date on top)
    pivot_df = pivot_df.sort_index(ascending=False)

    # Limit number of rows to max_rows (if you want scrolling to work well)
    if len(pivot_df) > max_rows:
        pivot_df = pivot_df.head(max_rows)  # take latest max_rows

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

    # Annotations with median values inside cells
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
        yaxis=dict(autorange='reversed'),  # Reverse so latest is on top
        template='plotly_dark',
        margin=dict(l=150, r=20, t=120, b=100),
        height=700,
        annotations=annotations,
    )

    return fig

def main():
    st.set_page_config(page_title="Economic Recession Indicator Heatmap", layout="wide", page_icon="📊")
    st.title("Economic Recession Indicator Heatmap")

    df = load_data()

    st.markdown(
        """
        <style>
        /* Scrollable container for the plot */
        .scrollable-plotly {
            max-height: 700px;
            overflow-y: auto;
        }
        /* Fix the plotly container inside Streamlit */
        .scrollable-plotly > div {
            min-height: 700px;
        }
        </style>
        """, unsafe_allow_html=True
    )

    with st.container():
        st.markdown('<div class="scrollable-plotly">', unsafe_allow_html=True)
        fig = create_heatmap(df, max_rows=100)  # Show last 100 months max, scroll container allows viewing all
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
