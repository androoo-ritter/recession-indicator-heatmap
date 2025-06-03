import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQSg0j0ZpwXjDgSS1IEA4MA2-SwTbAhNgy8hqQVveM4eeWWIg6zxgMq-NpUIZBzQvssY2LsSo3kfc8x/pub?gid=995887444&single=true&output=csv"
TTM_ATTRS = ['Bank Credit', 'Loans and Leases', 'M1', 'M2']
YOY_ATTRS = ['SP500', 'Credit Card Delinquency']

THRESHOLDS = {
    '3-Month': {'green': 2.5, 'yellow': 4.5, 'red_expl': 'Excessively high short-term interest rates', 'inverted': False},
    '20-Year': {'green': 3.5, 'yellow': 4.5, 'red_expl': 'Long-term rates may signal inflation or instability', 'inverted': False},
    '30-Year': {'green': 3.5, 'yellow': 4.5, 'red_expl': 'Long-term borrowing costs high', 'inverted': False},
    'Bank Credit': {'green': 17500, 'yellow': 16500, 'red_expl': 'Contraction in lending activity (billions)', 'inverted': True},
    'Claims': {'green': 250000, 'yellow': 300000, 'red_expl': 'Spike in unemployment claims', 'inverted': False},
    'Consumer Sentiment': {'green': 80, 'yellow': 60, 'red_expl': 'Low consumer confidence', 'inverted': True},
    'Continued Claims': {'green': 1800000, 'yellow': 2400000, 'red_expl': 'Extended unemployment', 'inverted': False},
    'Core CPI': {'green': 2.0, 'yellow': 3.5, 'red_expl': 'Elevated core inflation', 'inverted': False},
    'CPI': {'green': 2.0, 'yellow': 3.5, 'red_expl': 'Elevated inflation', 'inverted': False},
    'Credit Card Delinquency': {'green': 2.5, 'yellow': 4.0, 'red_expl': 'Consumers struggling with debt', 'inverted': False},
    'Loans and Leases': {'green': 12000, 'yellow': 11000, 'red_expl': 'Decrease in bank lending (billions)', 'inverted': True},
    'M1': {'green': 17500, 'yellow': 16500, 'red_expl': 'Shrinking money supply (billions)', 'inverted': True},
    'M2': {'green': 21000, 'yellow': 19000, 'red_expl': 'Shrinking broader money supply (billions)', 'inverted': True},
    'Mortgage Delinquency': {'green': 2.0, 'yellow': 4.0, 'red_expl': 'Housing distress', 'inverted': False},
    'Payrolls': {'green': 150, 'yellow': 0, 'red_expl': 'Significant job loss (thousands)', 'inverted': True},
    'Real FFR': {'green': 3.0, 'yellow': 4.5, 'red_expl': 'Restrictive monetary policy', 'inverted': False},
    'Real GDP': {'green': 1.5, 'yellow': 0.0, 'red_expl': 'Economic contraction', 'inverted': True},
    'Retail Sales': {'green': 680000, 'yellow': 660000, 'red_expl': 'Declining consumer spending (millions)', 'inverted': True},
    'Sahm': {'green': 0.4, 'yellow': 0.7, 'red_expl': 'Likely start of a recession', 'inverted': False},
    'SP500': {'green': 10.0, 'yellow': 0.0, 'red_expl': 'Market decline (YoY %)', 'inverted': True},
    'Transport Jobs': {'green': 6200, 'yellow': 6000, 'red_expl': 'Demand-side weakness (thousands)', 'inverted': True},
    'Unemployment': {'green': 4.0, 'yellow': 5.5, 'red_expl': 'Labor market deterioration', 'inverted': False},
    'USHY': {'green': 5.0, 'yellow': 7.0, 'red_expl': 'Risk premium surging', 'inverted': False},
    'USIG': {'green': 3.0, 'yellow': 4.5, 'red_expl': 'Credit stress in investment grade', 'inverted': False},
    'VIX': {'green': 20, 'yellow': 30, 'red_expl': 'High market volatility', 'inverted': False},
}

ATTRIBUTE_LABELS = {
    '3-Month': '3-Month Treasury',
    '20-Year': '20-Year Treasury',
    '30-Year': '30-Year Treasury',
    'Bank Credit': 'Bank Credit (Billions)',
    'Claims': 'Claims',
    'Consumer Sentiment': 'Consumer Sentiment',
    'Continued Claims': 'Continued Claims',
    'Core CPI': 'Core CPI',
    'CPI': 'CPI',
    'Credit Card Delinquency': 'CC Delinquency (%)',
    'Loans and Leases': 'Loans & Leases (Billions)',
    'M1': 'M1 (Billions)',
    'M2': 'M2 (Billions)',
    'Mortgage Delinquency': 'Mortgage Delinquency Rate',
    'Payrolls': 'Nonfarm Payrolls (Thousands)',
    'Real FFR': 'Fed Funds Rate',
    'Real GDP': 'Real GDP',
    'Retail Sales': 'Retail Sales (Millions)',
    'Sahm': 'Sahm',
    'SP500': 'S&P 500',
    'Transport Jobs': 'Transport Jobs (Thousands)',
    'Unemployment': 'Unemployment Rate (%)',
    'USHY': 'US HY Index',
    'USIG': 'US IG Index',
    'VIX': 'VIX',
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
    "Loans and Leases": "https://fred.stlouisfed.org/series/TOTLL",
    "M1": "https://fred.stlouisfed.org/series/M1SL",
    "M2": "https://fred.stlouisfed.org/series/M2SL",
    "Mortgage Delinquency": "https://fred.stlouisfed.org/series/DRSFRMACBS",
    "Payrolls": "https://fred.stlouisfed.org/series/PAYEMS",
    "Real FFR": "https://fred.stlouisfed.org/series/FEDFUNDS",
    "Real GDP": "https://fred.stlouisfed.org/series/A191RL1Q225SBEA",
    "Retail Sales": "https://fred.stlouisfed.org/series/RSXFS",
    "Sahm": "https://fred.stlouisfed.org/series/SAHMREALTIME",
    "SP500": "https://fred.stlouisfed.org/series/SP500",
    "Transport Jobs": "https://fred.stlouisfed.org/series/CES4348400001",
    "Unemployment": "https://fred.stlouisfed.org/series/UNRATE",
    "USHY": "https://fred.stlouisfed.org/series/BAMLH0A0HYM2",
    "USIG": "https://fred.stlouisfed.org/series/BAMLC0A0CM",
    "VIX": "https://fred.stlouisfed.org/series/VIXCLS",
}

PUBLICATION_FREQUENCIES = {
    "3-Month": "Daily",
    "20-Year": "Daily",
    "30-Year": "Daily",
    "Bank Credit": "Weekly",
    "Claims": "Weekly",
    "Consumer Sentiment": "Monthly",
    "Continued Claims": "Weekly",
    "Core CPI": "Monthly",
    "CPI": "Monthly",
    "Credit Card Delinquency": "Quarterly",
    "Loans and Leases": "Weekly",
    "M1": "Monthly",
    "M2": "Monthly",
    "Mortgage Delinquency": "Quarterly",
    "Payrolls": "Monthly",
    "Real FFR": "Monthly",
    "Real GDP": "Quarterly",
    "Retail Sales": "Monthly",
    "Sahm": "Monthly",
    "SP500": "Daily",
    "Transport Jobs": "Monthly",
    "Unemployment": "Monthly",
    "USHY": "Daily",
    "USIG": "Daily",
    "VIX": "Daily",
}

def format_value(val, attr=None):
    if pd.isna(val):
        return "N/A"
    if isinstance(val, (int, float)):
        percent_attrs = ['Credit Card Delinquency', 'SP500']
        if attr in percent_attrs:
            return f"{val:.2f}%"
        elif abs(val) >= 1000:
            return f"{val:,.0f}"
        else:
            return f"{val:.2f}"
    return str(val)

@st.cache_data
def load_and_preprocess_data():
    """Load and preprocess Combined Data CSV."""
    try:
        logger.info("Loading Combined Data CSV")
        df = pd.read_csv(CSV_URL)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        df = df.dropna(subset=['Date', 'Value', 'Attribute'])
        df['MonthYear'] = df['Date'].dt.to_period('M').dt.to_timestamp()
        
        logger.info(f"Loaded {len(df)} rows of data")
        
        # Aggregate to monthly averages to handle daily/weekly data
        monthly_avg = df.groupby(['Attribute', 'MonthYear'])['Value'].mean().reset_index()
        
        # Initialize results
        attributes = monthly_avg['Attribute'].unique()
        months = pd.date_range(
            monthly_avg['MonthYear'].min(), 
            monthly_avg['MonthYear'].max(), 
            freq='MS'
        )
        results = []
        
        with st.progress(0, text="Preprocessing data..."):
            total_steps = len(attributes)
            for idx, attr in enumerate(attributes):
                attr_df = monthly_avg[monthly_avg['Attribute'] == attr].set_index('MonthYear')
                calc_type = 'TTM' if attr in TTM_ATTRS else 'YoY' if attr in YOY_ATTRS else 'Median'
                
                for month in months:
                    if calc_type == 'TTM':
                        # Trailing 12-month average
                        start = month - pd.offsets.MonthBegin(12)
                        window = attr_df.loc[start:month]['Value']
                        if len(window) >= 12:
                            value = window.mean().round(2)
                        else:
                            value = np.nan
                    elif calc_type == 'YoY':
                        # Year-over-year % change
                        current = attr_df.loc[month:month]['Value']
                        prior = attr_df.loc[month - pd.offsets.MonthBegin(12):month - pd.offsets.MonthBegin(12)]['Value']
                        if not current.empty and not prior.empty and prior.iloc[0] != 0:
                            value = ((current.iloc[0] - prior.iloc[0]) / prior.iloc[0] * 100).round(2)
                        else:
                            value = np.nan
                    else:
                        # Median (monthly average)
                        current = attr_df.loc[month:month]['Value']
                        value = current.mean().round(2) if not current.empty else np.nan
                    
                    results.append({
                        'Attribute': attr,
                        'MonthYear': month,
                        'Value': value,
                        'CalculationType': calc_type
                    })
                
                # Update progress
                st.progress((idx + 1) / total_steps, text=f"Processing {attr}...")
        
        precomputed_df = pd.DataFrame(results)
        precomputed_df = precomputed_df.dropna(subset=['Value'])
        logger.info(f"Precomputed {len(precomputed_df)} rows")
        return precomputed_df
    except Exception as e:
        logger.error(f"Error loading/preprocessing data: {e}")
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()

def color_for_value(attr, val):
    if pd.isna(val):
        return 'gray'
    t = THRESHOLDS.get(attr)
    if not t:
        return 'gray'
    if t.get('inverted', False):
        if val >= t['green']:
            return 'green'
        elif val >= t['yellow']:
            return 'yellow'
        else:
            return 'red'
    else:
        if val <= t['green']:
            return 'green'
        elif val <= t['yellow']:
            return 'yellow'
        else:
            return 'red'

def create_heatmap(df, selected_months):
    try:
        logger.info("Starting heatmap creation")
        full_df = df[df['MonthYear'].isin(selected_months)]
        if full_df.empty:
            logger.warning("No data available for selected months")
            st.warning("No data available for the selected months.")
            return None

        pivot_df = full_df.pivot(index='MonthYear', columns='Attribute', values='Value').sort_index(ascending=False)
        logger.info(f"Pivot table created with {len(pivot_df)} rows")

        colors = []
        for dt in pivot_df.index:
            colors.append([color_for_value(attr, pivot_df.at[dt, attr]) for attr in pivot_df.columns])

        hover_text = []
        for dt in pivot_df.index:
            row = []
            dt_str = dt.strftime("%b %Y")
            for attr in pivot_df.columns:
                val = pivot_df.at[dt, attr]
                val_str = format_value(val, attr=attr)
                calc_type = "TTM" if attr in TTM_ATTRS else "YoY %" if attr in YOY_ATTRS else "Median"
                row.append(f"<b>{ATTRIBUTE_LABELS.get(attr, attr)}</b><br>{dt_str}<br>{calc_type}: {val_str}")
            hover_text.append(row)

        color_map = {'gray': 0.0, 'green': 0.001, 'yellow': 0.5, 'red': 1.0}
        z_colors = np.array([[color_map.get(c, 0.0) for c in row] for row in colors])

        num_rows = len(pivot_df)
        min_height = 600
        max_height = 1600
        default_row_height = 40
        total_height = max(min_height, min(max_height, default_row_height * num_rows))
        font_size = 10 if num_rows <= 12 else 8 if num_rows <= 24 else 6

        fig = go.Figure(data=go.Heatmap(
            z=z_colors,
            x=[ATTRIBUTE_LABELS.get(attr, attr) for attr in pivot_df.columns],
            y=[d.strftime("%b %Y") for d in pivot_df.index],
            text=hover_text,
            hoverinfo='text',
            colorscale=[
                [0.0, 'lightgray'],
                [0.001, 'green'],
                [0.5, 'yellow'],
                [1.0, 'red']
            ],
            showscale=False,
            xgap=2,
            ygap=2
        ))

        annotations = []
        for y_idx, dt in enumerate(pivot_df.index):
            for x_idx, attr in enumerate(pivot_df.columns):
                val = pivot_df.at[dt, attr]
                if pd.notnull(val):
                    annotations.append(dict(
                        x=ATTRIBUTE_LABELS.get(attr, attr),
                        y=dt.strftime("%b %Y"),
                        text=format_value(val, attr=attr),
                        showarrow=False,
                        font=dict(color="black", size=font_size),
                        xanchor="center",
                        yanchor="middle"
                    ))

        fig.update_layout(
            xaxis=dict(side='top', tickfont=dict(size=font_size)),
            yaxis=dict(autorange='reversed', tickfont=dict(size=font_size)),
            annotations=annotations,
            margin=dict(l=150, r=20, t=120, b=40),
            template='plotly_white',
            height=total_height
        )

        logger.info("Heatmap figure created successfully")
        return fig
    except Exception as e:
        logger.error(f"Error creating heatmap: {e}")
        st.error(f"Failed to create heatmap: {e}")
        return None

def main():
    st.set_page_config(page_title="MacroGamut Economic Recession Indicator", layout="wide")

    if st.button("🔄 Refresh Data from Source"):
        st.cache_data.clear()
        st.experimental_rerun()

    st.markdown("""
        <div style='display: flex; align-items: center; gap: 15px; margin-bottom: -10px;'>
            <img src='https://raw.githubusercontent.com/androoo-ritter/recession-indicator-heatmap/main/logo.png' width='60'/>
            <h1 style='margin: 0;'>MacroGamut Economic Recession Indicator</h1>
        </div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ Disclaimer", expanded=False):
        st.markdown("""
        This dashboard uses publicly available economic time series data from the [Federal Reserve Economic Data (FRED)](https://fred.stlouisfed.org/) database.  
        It is intended for **educational purposes only** and **should not be interpreted as financial or investment advice**.  
        Please independently verify any figures you use from this page.  

        Data is aggregated as follows:
        - **Bank Credit, Loans and Leases, M1, M2**: Trailing Twelve Months (TTM) average
        - **SP500, Credit Card Delinquency**: Year-over-Year (YoY) % change
        - **Other indicators**: Median value for each respective month
        """)

    with st.expander("🟩 Color Legend", expanded=False):
        st.markdown("""
        - **🟩 Green**: Healthy/expected range  
        - **🟨 Yellow**: Caution  
        - **🟥 Red**: Warning / likely signal  
        - **⬜ Grey**: No data available for that month
        """)

    with st.expander("🎯 View Thresholds by Data Point", expanded=False):
        threshold_df = pd.DataFrame([
            {
                "Data Point": ATTRIBUTE_LABELS.get(attr, attr),
                "Green": f"≥ {v['green']}" if v.get('inverted') else f"≤ {v['green']}",
                "Yellow": f"≥ {v['yellow']}" if v.get('inverted') else f"≤ {v['yellow']}",
                "Red": f"< {v['yellow']}" if v.get('inverted') else f"> {v['yellow']}",
                "Explanation": v["red_expl"]
            }
            for attr, v in THRESHOLDS.items()
        ])
        st.dataframe(threshold_df, use_container_width=True)

    with st.expander("📎 View FRED Data Source Reference", expanded=False):
        st.markdown("Each metric below links directly to its FRED series page.")
        st.markdown(
            "<table><thead><tr><th>Data Point</th><th>FRED Link</th><th>Publication Frequency</th></tr></thead><tbody>" +
            "".join(
                f"<tr><td>{ATTRIBUTE_LABELS.get(dp, dp)}</td><td><a href='{url}' target='_blank'>{url}</a></td><td>{PUBLICATION_FREQUENCIES.get(dp, 'N/A')}</td></tr>"
                for dp, url in FRED_SOURCES.items()
            ) +
            "</tbody></table>",
            unsafe_allow_html=True
        )

    with st.spinner("Loading data..."):
        df = load_and_preprocess_data()

    if df.empty:
        st.error("No data loaded. Please check the CSV URL or try refreshing.")
        return

    all_months = pd.date_range(df['MonthYear'].min(), df['MonthYear'].max(), freq='MS').to_period('M').to_timestamp()
    all_months = sorted(all_months, reverse=True)
    month_labels = [d.strftime("%b %Y") for d in all_months]
    month_map = dict(zip(month_labels, all_months))

    selected_labels = st.multiselect(
        "Filter by Month-Year:",
        options=month_labels,
        default=month_labels[:36]
    )
    selected_months = [month_map[label] for label in selected_labels] if selected_labels else all_months

    with st.spinner("Generating heatmap..."):
        fig = create_heatmap(df, selected_months)
        if fig is not None:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Failed to generate heatmap. Please check the logs or try a different month selection.")

if __name__ == "__main__":
    main()
