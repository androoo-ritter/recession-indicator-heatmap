Skip to content
Navigation Menu
androoo-ritter
recession-indicator-heatmap

Type / to search
Code
Issues
Pull requests
Actions
Projects
Wiki
Security
Insights
Settings
Commit 36c6514
androoo-ritter
androoo-ritter
authored
10 minutes ago
Verified
Update app.py
main
1 parent 
1eb4140
 commit 
36c6514
File tree
Filter files…
app.py
1 file changed
+20
-45
lines changed
Search within code
 
‎app.py
+20
-45
Lines changed: 20 additions & 45 deletions
Original file line number	Diff line number	Diff line change
@@ -1,4 +1,4 @@
logic: import streamlit as st
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
@@ -34,32 +34,7 @@
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
    # (same source dictionary, unchanged)
}

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQSg0j0ZpwXjDgSS1IEA4MA2-SwTbAhNgy8hqQVveM4eeWWIg6zxgMq-NpUIZBzQvssY2LsSo3kfc8x/pub?gid=995887444&single=true&output=csv"
@@ -111,16 +86,21 @@
            row.append(f"<b>{attr}</b><br>{dt_str}<br>Median: {val_str}")
        hover_text.append(row)

    color_map = {'green': 0, 'yellow': 0.5, 'red': 1, 'gray': 0.25}
    z_colors = np.array([[color_map.get(c, 0.25) for c in row] for row in colors])
    color_map = {'gray': 0.0, 'green': 0.001, 'yellow': 0.5, 'red': 1.0}
    z_colors = np.array([[color_map.get(c, 0.0) for c in row] for row in colors])

    fig = go.Figure(data=go.Heatmap(
        z=z_colors,
        x=pivot_df.columns,
        y=[d.strftime("%b %Y") for d in pivot_df.index],
        text=hover_text,
        hoverinfo='text',
        colorscale=[[0, 'green'], [0.5, 'yellow'], [1, 'red']],
        colorscale=[
            [0.0, 'lightgray'],   # Grey for missing data
            [0.001, 'green'],
            [0.5, 'yellow'],
            [1.0, 'red']
        ],
        showscale=False,
        xgap=2,
        ygap=2
@@ -147,68 +127,63 @@
        annotations=annotations,
        margin=dict(l=150, r=20, t=120, b=40),
        template='plotly_white',
        height=min(1600, 40 * len(pivot_df))  # dynamic height
        height=min(1600, 40 * len(pivot_df))
    )

    return fig

def main():
    st.set_page_config(page_title="MacroGamut Economic Recession Indicator", layout="wide")
    st.image("logo.png", width=70)
    st.markdown("<h1 style='margin-top: -60px;'>MacroGamut Economic Recession Indicator</h1>", unsafe_allow_html=True)

    st.markdown("""
        <div style='display: flex; align-items: center; gap: 10px; margin-bottom: -20px;'>
            <img src="https://github.com/androoo-ritter/recession-indicator-heatmap/blob/main/logo.png?raw=true" width="40" style="margin: 0;" />
            <h1 style='margin: 0;'>MacroGamut Economic Recession Indicator</h1>
        </div>
    """, unsafe_allow_html=True)
    with st.expander("📝 Disclaimer", expanded=False):
    with st.expander("ℹ️ Disclaimer", expanded=False):
        st.markdown("""
        This dashboard uses publicly available economic time series data from the [Federal Reserve Economic Data (FRED)](https://fred.stlouisfed.org/) database.  
        It is intended for **educational purposes only** and **should not be interpreted as financial or investment advice**.  
        Please independently verify any figures you use from this page.  
        
        Given that each economic indicator is published at different intervals (daily, monthly, quarterly, etc.),  
        this tool aggregates data by computing the **median value for each indicator per month**.
        """)

    with st.expander("🎨 Color Legend", expanded=False):
    with st.expander("🟩 Color Legend", expanded=False):
        st.markdown("""
        - 🟩 **Green**: Healthy/expected range  
        - 🟨 **Yellow**: Caution  
        - 🟥 **Red**: Warning / likely signal  
        - ⬜ **Grey**: No data available for that month
        - **🟩 Green**: Healthy/expected range  
        - **🟨 Yellow**: Caution  
        - **🟥 Red**: Warning / likely signal  
        - **⬜ Grey**: No data available for that month
        """)

    with st.expander("🎯 View Thresholds by Data Point", expanded=False):
        threshold_df = pd.DataFrame([
            {"Data Point": attr, "Green ≤": v["green"], "Yellow ≤": v["yellow"], "Red =": f">{v['yellow']}", "Explanation": v['red_expl']}
            for attr, v in THRESHOLDS.items()
        ])
        st.dataframe(threshold_df, use_container_width=True)

    with st.expander("📎 View FRED Data Source Reference", expanded=False):
        st.markdown("Each metric below links directly to its FRED series page.")
        st.markdown("<table><thead><tr><th>Data Point</th><th>FRED Link</th></tr></thead><tbody>" + "".join(
            f"<tr><td>{dp}</td><td><a href='{url}' target='_blank'>{url}</a></td></tr>" 
            for dp, url in FRED_SOURCES.items()) + "</tbody></table>", unsafe_allow_html=True)

    df = load_data()

    all_months = pd.date_range(df['MonthYear'].min(), df['MonthYear'].max(), freq='MS').to_period('M').to_timestamp()
    all_months = sorted(all_months, reverse=True)
    month_labels = [d.strftime("%b %Y") for d in all_months]
    month_map = dict(zip(month_labels, all_months))

    selected_labels = st.multiselect(
        "Filter by Month-Year:",
        options=month_labels,
        default=month_labels[:36]  # Latest 3 years
    )
    selected_months = [month_map[label] for label in selected_labels] if selected_labels else all_months

    fig = create_heatmap(df, selected_months)
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
0 commit comments
Comments
0
 (0)
Comment
You're not receiving notifications from this thread.

