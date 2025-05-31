import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import logging

# Set up logging to debug issues
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# [THRESHOLDS, ATTRIBUTE_LABELS, FRED_SOURCES, PUBLICATION_FREQUENCIES remain unchanged from previous version]
THRESHOLDS = {
    '3-Month': {'red': 2.5, 'yellow': 4.5, 'red_expl': 'Low short-term interest rates (good)', 'inverted': True},
    '20-Year': {'red': 3.5, 'yellow': 4.5, 'red_expl': 'Low long-term rates (good)', 'inverted': True},
    '30-Year': {'red': 3.5, 'yellow': 4.5, 'red_expl': 'Low long-term borrowing costs (good)', 'inverted': True},
    'Bank Credit': {'red': 18000, 'yellow': 16500, 'red_expl': 'Strong lending activity (billions, TTM)', 'inverted': False},
    'Claims': {'red': 250000, 'yellow': 300000, 'red_expl': 'Low unemployment claims (good)', 'inverted': True},
    'Consumer Sentiment': {'red': 80, 'yellow': 60, 'red_expl': 'High consumer confidence (good)', 'inverted': False},
    'Continued Claims': {'red': 1800000, 'yellow': 2400000, 'red_expl': 'Low extended unemployment (good)', 'inverted': True},
    'Core CPI': {'red': 2.0, 'yellow': 3.5, 'red_expl': 'Low core inflation (good)', 'inverted': True},
    'CPI': {'red': 2.0, 'yellow': 3.5, 'red_expl': 'Low inflation (good)', 'inverted': True},
    'Credit Card Delinquency': {'red': 0.0, 'yellow': 5.0, 'red_expl': 'Stable or declining delinquency (%, YoY)', 'inverted': True},
    'Loans and Leases': {'red': 12500, 'yellow': 11000, 'red_expl': 'Strong bank lending (billions, TTM)', 'inverted': False},
    'M1': {'red': 18000, 'yellow': 16500, 'red_expl': 'Growing money supply (billions, TTM)', 'inverted': False},
    'M2': {'red': 21500, 'yellow': 19000, 'red_expl': 'Growing broader money supply (billions, TTM)', 'inverted': False},
    'Mortgage Delinquency': {'red': 2.0, 'yellow': 4.0, 'red_expl': 'Low housing distress (good)', 'inverted': True},
    'Payrolls': {'red': 150, 'yellow': 0, 'red_expl': 'Strong job growth (thousands, good)', 'inverted': False},
    'Real FFR': {'red': 3.0, 'yellow': 4.5, 'red_expl': 'Accommodative monetary policy (good)', 'inverted': True},
    'Real GDP': {'red': 1.5, 'yellow': 0.0, 'red_expl': 'Economic expansion (good)', 'inverted': False},
    'Retail Sales': {'red': 680000, 'yellow': 660000, 'red_expl': 'Strong consumer spending (millions, good)', 'inverted': False},
    'Sahm': {'red': 0.4, 'yellow': 0.7, 'red_expl': 'Low recession risk (good)', 'inverted': True},
    'SP500': {'red': 10.0, 'yellow': 0.0, 'red_expl': 'Strong market growth (%, YoY)', 'inverted': False},
    'Transport Jobs': {'red': 2.0, 'yellow': -1.0, 'red_expl': 'Growing transport sector (%, YoY)', 'inverted': False},
    'Unemployment': {'red': 4.0, 'yellow': 5.5, 'red_expl': 'Strong labor market (good)', 'inverted': True},
    'USHY': {'red': 5.0, 'yellow': 7.0, 'red_expl': 'Low risk premium (good)', 'inverted': True},
    'USIG': {'red': 3.0, 'yellow': 4.5, 'red_expl': 'Low credit stress (good)', 'inverted': True},
    'VIX': {'red': 20, 'yellow': 30, 'red_expl': 'Low market volatility (good)', 'inverted': True},
    '3MOPayrolls': {'red': 150, 'yellow': 100, 'red_expl': 'Strong recent job momentum (good)', 'inverted': False},
    '2YearTreasury': {'red': 2.5, 'yellow': 4.0, 'red_expl': 'Low short-term rates (good, TTM)', 'inverted': True},
    '10YearTreasury': {'red': 3.0, 'yellow': 4.5, 'red_expl': 'Low mid-term rates (good, TTM)', 'inverted': True},
    'ConstructionJobs': {'red': 2.0, 'yellow': -1.0, 'red_expl': 'Growing construction sector (%, YoY)', 'inverted': False},
    '2s10s': {'red': 0.5, 'yellow': 0.0, 'red_expl': 'Positive yield curve (good)', 'inverted': False},
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
    '3MOPayrolls': '3-Month Payroll Avg (Thousands)',
    '2YearTreasury': '2-Year Treasury',
    '10YearTreasury': '10-Year Treasury',
    'ConstructionJobs': 'Construction Jobs',
    '2s10s': '2s10s Spread',
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
    '3MOPayrolls': 'Monthly',
    '2YearTreasury': 'Daily',
    '10YearTreasury': 'Daily',
    'ConstructionJobs': 'Monthly',
    '2s10s': 'Daily'
}

def format_value(val):
    if pd.isna(val):
        return "N/A"
    if isinstance(val, (int, float)):
        if abs(val) >= 1000:
            return f"{val:,.0f}"
        else:
            return f"{val:.2f}%"
    return str(val)

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQSg0j0ZpwXjDgSS1IEA4MA2-SwTbAhNgy8hqQVveM4eeWWIg6zxgMq-NpUIZBzQvssY2LsSo3kfc8x/pub?gid=995887444&single=true&output=csv"

@st.cache_data
def load_data():
    try:
        logger.info("Loading data from CSV")
        df = pd.read_csv(CSV_URL)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        df = df.dropna(subset=['Date', 'Value'])
        df['MonthYear'] = df['Date'].dt.to_period('M').dt.to_timestamp()
        logger.info(f"Loaded {len(df)} rows of data")
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()

def color_for_value(attr, val):
    if pd.isna(val):
        return 'gray'
    t = THRESHOLDS.get(attr)
    if not t:
        return 'gray'
    if t.get('inverted', False):
        if val <= t['red']:
            return 'red'  # Good
        elif val <= t['yellow']:
            return 'yellow'  # Caution
        else:
            return 'green'  # Bad
    else:
        if val >= t['red']:
            return 'red'  # Good
        elif val >= t['yellow']:
            return 'yellow'  # Caution
        else:
            return 'green'  # Bad

def calculate_ttm(df, attr, month):
    try:
        attr_df = df[df['Attribute'] == attr][['MonthYear', 'Value']].copy()
        end_date = month
        start_date = end_date - pd.offsets.MonthBegin(12)
        window_df = attr_df[(attr_df['MonthYear'] >= start_date) & (attr_df['MonthYear'] <= end_date)]
        if len(window_df) >= 12:
            return window_df['Value'].mean().round(2)
        return np.nan
    except Exception as e:
        logger.error(f"Error calculating TTM for {attr} at {month}: {e}")
        return np.nan

def calculate_yoy(df, attr, month):
    try:
        attr_df = df[df['Attribute'] == attr][['MonthYear', 'Value']].copy()
        current = attr_df[attr_df['MonthYear'] == month]['Value']
        last_year = attr_df[attr_df['MonthYear'] == (month - pd.offsets.MonthBegin(12))]['Value']
        if not current.empty and not last_year.empty:
            current_val = current.iloc[0]
            last_year_val = last_year.iloc[0]
            if last_year_val != 0:
                return ((current_val - last_year_val) / last_year_val * 100).round(2)
        return np.nan
    except Exception as e:
        logger.error(f"Error calculating YoY for {attr} at {month}: {e}")
        return np.nan

def create_heatmap(df, selected_months):
    try:
        logger.info("Starting heatmap creation")
        attributes = df['Attribute'].unique()
        all_months = pd.date_range(df['MonthYear'].min(), df['MonthYear'].max(), freq='MS').to_period('M').to_timestamp()
        logger.info(f"Processing {len(attributes)} attributes and {len(all_months)} months")

        # Precompute TTM and YoY values to improve performance
        ttm_attrs = ['Bank Credit', 'Loans and Leases', 'M1', 'M2', '2YearTreasury', '10YearTreasury']
        yoy_attrs = ['Credit Card Delinquency', 'SP500', 'Transport Jobs', 'ConstructionJobs']
        processed_values = []

        for attr in attributes:
            attr_df = df[df['Attribute'] == attr][['MonthYear', 'Value']].copy()
            for month in all_months:
                if attr in ttm_attrs:
                    value = calculate_ttm(df, attr, month)
                elif attr in yoy_attrs:
                    value = calculate_yoy(df, attr, month)
                else:
                    month_df = attr_df[attr_df['MonthYear'] == month]
                    value = month_df['Value'].median().round(2) if not month_df.empty else np.nan
                processed_values.append({'Attribute': attr, 'MonthYear': month, 'Value': value})

        full_df = pd.DataFrame(processed_values)
        full_df = full_df[full_df['MonthYear'].isin(selected_months)]
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
                val_str = format_value(val)
                calc_type = "TTM" if attr in ttm_attrs else "YoY %" if attr in yoy_attrs else "Median"
                row.append(f"<b>{ATTRIBUTE_LABELS.get(attr, attr)}</b><br>{dt_str}<br>{calc_type}: {val_str}")
            hover_text.append(row)

        color_map = {'gray': 0.0, 'red': 0.001, 'yellow': 0.5, 'green': 1.0}
        z_colors = np.array([[color_map.get(c, 0.0) for c in row] for row in colors])

        # Simplified height adjustment
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
                [0.001, 'red'],
                [0.5, 'yellow'],
                [1.0, 'green']
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
                        text=format_value(val),
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

        Given that each economic indicator is published at different intervals (daily, monthly, quarterly, etc.),  
        this tool aggregates data as follows:
        - **Bank Credit, Loans and Leases, M1, M2, 2-Year Treasury, 10-Year Treasury**: Trailing Twelve Months (TTM) average
        - **Credit Card Delinquency, S&P 500, Transport Jobs, Construction Jobs**: Year-over-Year (YoY) % change
        - **Other indicators**: Median value for each respective month
        """)

    with st.expander("🟥 Color Legend", expanded=False):
        st.markdown("""
        - **🟥 Red**: Good/healthy range  
        - **🟨 Yellow**: Caution  
        - **🟩 Green**: Bad/warning signal  
        - **⬜ Grey**: No data available for that month
        """)

    with st.expander("🎯 View Thresholds by Data Point", expanded=False):
        threshold_df = pd.DataFrame([
            {
                "Data Point": ATTRIBUTE_LABELS.get(attr, attr),
                "Red (Good)": f"≤ {v['red']}" if v.get('inverted') else f"≥ {v['red']}",
                "Yellow (Caution)": f"≤ {v['yellow']}" if v.get('inverted') else f"≥ {v['yellow']}",
                "Green (Bad)": f"> {v['yellow']}" if v.get('inverted') else f"< {v['yellow']}",
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

    df = load_data()
    if df.empty:
        st.error("No data loaded. Please check the data source or try refreshing.")
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
