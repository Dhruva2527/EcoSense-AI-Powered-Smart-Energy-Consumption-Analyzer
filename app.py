import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.express as px

# Imports matching your team's module structure
from modules.data_cleaner import clean_energy_data, aggregate_daily, compute_summary_analytics
from modules.anomaly_detection import detect_anomalies
from modules.prediction import train_and_forecast
from modules.cost_estimator import estimate_electricity_cost
from modules.recommendations import calculate_energy_score_and_recs

st.set_page_config(
    page_title="EcoSense | Smart Energy Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Load CSS safely (fallback to default styling if CSS file is missing)
CSS_PATH = Path(__file__).parent / "assets" / "style.css"
if CSS_PATH.exists():
    st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
else:
    st.markdown(
        """
        <style>
        .metric-card { background-color: #f8f9fa; border-radius: 8px; padding: 15px; margin-bottom: 10px; }
        .panel { background-color: #ffffff; border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; margin-bottom: 15px; }
        .insight-box { background-color: #e8f4f8; padding: 12px; border-radius: 6px; border-left: 4px solid #17a2b8; }
        .summary-line { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f3f5; }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Helper function to generate built-in sample data
def make_sample_data():
    dates = pd.date_range(start="2026-10-01", periods=30, freq="D")
    np.random.seed(42)
    values = np.random.uniform(8.0, 11.5, size=30)
    # Inject deliberate spikes for testing demo
    values[4] = 24.5  # Oct 5 Spike
    values[17] = 28.2 # Oct 18 Spike
    df_sample = pd.DataFrame({'timestamp': dates, 'consumption_kwh': np.round(values, 2)})
    return df_sample

# Session State Initialization
if "energy_df" not in st.session_state:
    st.session_state.energy_df = make_sample_data()
if "source_name" not in st.session_state:
    st.session_state.source_name = "Built-in demonstration dataset"
if "tariff" not in st.session_state:
    st.session_state.tariff = 7.0

def fmt_num(value, digits=1):
    return f"{value:,.{digits}f}"

def metric_card(label, value, suffix="", note="", icon="⚡"):
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-top"><span>{icon}</span><span class="metric-label">{label}</span></div>
          <div class="metric-value" style="font-size: 1.8rem; font-weight: bold;">{value} <small style="font-size: 1rem;">{suffix}</small></div>
          <div class="metric-note" style="color: #6c757d; font-size: 0.85rem;">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Preprocessing current active data
cleaned_df = clean_energy_data(st.session_state.energy_df)
daily = aggregate_daily(cleaned_df)
metrics = compute_summary_analytics(daily)
cost_info = estimate_electricity_cost(metrics.get("total_kwh", 0), rate_per_kwh=st.session_state.tariff)

st.markdown(
    """
    <div class="app-header" style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0;">
      <div class="brand-wrap" style="display: flex; align-items: center; gap: 10px;">
        <div class="brand-mark" style="font-size: 2rem;">🌿</div>
        <div>
          <div class="brand-name" style="font-size: 1.5rem; font-weight: bold;">EcoSense</div>
          <div class="brand-sub" style="font-size: 0.75rem; color: #6c757d; letter-spacing: 1px;">SMART ENERGY INTELLIGENCE</div>
        </div>
      </div>
      <div class="header-status" style="color: #28a745; font-weight: 500;">🟢 DEMO SYSTEM ONLINE</div>
    </div>
    """,
    unsafe_allow_html=True,
)

nav_items = ["Overview", "Upload Data", "Analytics", "Anomaly Detection", "Predictions", "Recommendations"]
page = st.radio("Navigation", nav_items, horizontal=True, label_visibility="collapsed", key="main_navigation")
st.markdown('<hr style="margin: 10px 0 20px 0; border: none; border-top: 1px solid #e9ecef;">', unsafe_allow_html=True)

page_descriptions = {
    "Overview": "A clear snapshot of your household energy performance.",
    "Upload Data": "Import your electricity readings and validate the dataset.",
    "Analytics": "Explore consumption patterns across days and months.",
    "Anomaly Detection": "Find unusually high or low usage patterns in your readings.",
    "Predictions": "Estimate upcoming energy demand from historical consumption.",
    "Recommendations": "Turn your energy data into practical next steps.",
}
st.markdown(f'<div style="font-size: 0.75rem; color: #6c757d; font-weight: 600;">ENERGY WORKSPACE / {page.upper()}</div>', unsafe_allow_html=True)
st.markdown(f'<h2 style="margin-top:0;">{page}</h2><p style="color:#6c757d;">{page_descriptions[page]}</p>', unsafe_allow_html=True)

# ----------------- OVERVIEW TAB -----------------
if page == "Overview":
    st.markdown('<h4>Your energy at a glance <span style="font-size:0.8rem; background:#e9ecef; padding:3px 8px; border-radius:12px;">DEMO DATA</span></h4>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4, gap="small")
    with c1: metric_card("Total consumption", fmt_num(metrics["total_kwh"]), "kWh", "Across selected dataset", "⚡")
    with c2: metric_card("Daily average", fmt_num(metrics["daily_avg_kwh"]), "kWh", "Average per recorded day", "📊")
    with c3: metric_card("Highest usage", fmt_num(metrics["peak_usage_kwh"]), "kWh", f"Peak on {metrics['peak_date']}", "↗")
    with c4: metric_card("Estimated bill", f"₹{cost_info['total_estimated_cost']:,.0f}", "", f"At ₹{st.session_state.tariff:.2f} per kWh", "₹")

    left, right = st.columns([1.65, 1], gap="small")
    with left:
        st.markdown('<div class="panel"><b>Consumption trend</b><br><small style="color:#6c757d;">Daily electricity usage · kWh</small>', unsafe_allow_html=True)
        fig_trend = px.line(daily, x='timestamp', y='consumption_kwh', labels={'timestamp': 'Date', 'consumption_kwh': 'kWh'})
        st.plotly_chart(fig_trend, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><b>Usage summary</b><br><small style="color:#6c757d;">Key readings from your data</small><br><br>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary-line"><span>Lowest daily usage</span><b>{metrics["lowest_usage_kwh"]:.2f} kWh</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary-line"><span>Recorded days</span><b>{len(daily)}</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary-line"><span>Estimated monthly cost</span><b>₹{cost_info["total_estimated_cost"]:,.0f}</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary-line"><span>Data source</span><b>{st.session_state.source_name}</b></div>', unsafe_allow_html=True)
        st.markdown('<br><div class="insight-box"><b>💡 Eco insight</b><p style="margin:0; font-size:0.9rem;">Compare similar days and investigate repeated spikes before assuming they indicate waste.</p></div></div>', unsafe_allow_html=True)

# ----------------- UPLOAD DATA TAB -----------------
elif page == "Upload Data":
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<b>Upload electricity readings</b><br><small style="color:#6c757d;">CSV should contain a timestamp/date column and a consumption column.</small><br><br>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Choose a CSV file", type=["csv"])
    col_a, col_b = st.columns([1, 1])
    with col_a:
        tariff_input = st.number_input("Electricity tariff (₹ per kWh)", min_value=0.0, max_value=100.0, value=float(st.session_state.tariff), step=0.25)
    with col_b:
        st.markdown('<div style="background:#f8f9fa; padding:10px; border-radius:6px; font-size:0.85rem;"><b>Expected format</b><br><code>timestamp,consumption_kwh</code><br><code>2026-10-01 00:00,0.32</code></div>', unsafe_allow_html=True)
    
    if uploaded is not None:
        try:
            raw_uploaded = pd.read_csv(uploaded)
            candidate = clean_energy_data(raw_uploaded)
            st.success(f"Successfully read {len(candidate):,} valid records.")
            st.dataframe(candidate.head(12), use_container_width=True, hide_index=True)
            if st.button("Use this dataset", type="primary", use_container_width=True):
                st.session_state.energy_df = raw_uploaded
                st.session_state.source_name = uploaded.name
                st.session_state.tariff = tariff_input
                st.success("Dataset loaded. Open Overview or Analytics to explore it.")
                st.rerun()
        except Exception as exc:
            st.error(f"Could not load this file: {exc}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="panel"><b>Active Dataset Preview</b><br>', unsafe_allow_html=True)
    st.dataframe(daily.head(10), use_container_width=True, hide_index=True)
    st.download_button("Download active dataset CSV", daily.to_csv(index=False).encode("utf-8"), "ecosense_data.csv", "text/csv")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Restore demonstration dataset"):
        st.session_state.energy_df = make_sample_data()
        st.session_state.source_name = "Built-in demonstration dataset"
        st.rerun()

# ----------------- ANALYTICS TAB -----------------
elif page == "Analytics":
    period = st.selectbox("Aggregation", ["Daily", "Weekly", "Monthly"])
    if period == "Daily":
        chart_data = daily
    elif period == "Weekly":
        chart_data = cleaned_df.set_index("timestamp").resample("W")["consumption_kwh"].sum().reset_index()
    else:
        chart_data = cleaned_df.set_index("timestamp").resample("ME")["consumption_kwh"].sum().reset_index()
        
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    fig_analytics = px.bar(chart_data, x='timestamp', y='consumption_kwh', title=f"{period} Energy Consumption (kWh)")
    st.plotly_chart(fig_analytics, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)
    
    left, right = st.columns(2, gap="small")
    with left:
        st.markdown('<div class="panel"><b>Average Usage by Weekday</b>', unsafe_allow_html=True)
        weekday_avg = daily.groupby('day_of_week')['consumption_kwh'].mean().reset_index()
        days_map = {0:'Mon', 1:'Tue', 2:'Wed', 3:'Thu', 4:'Fri', 5:'Sat', 6:'Sun'}
        weekday_avg['day_name'] = weekday_avg['day_of_week'].map(days_map)
        fig_weekday = px.bar(weekday_avg, x='day_name', y='consumption_kwh', labels={'day_name':'Day', 'consumption_kwh':'Avg kWh'})
        st.plotly_chart(fig_weekday, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><b>Consumption Summary Table</b>', unsafe_allow_html=True)
        stats_table = pd.DataFrame({
            "Metric": ["Total", "Average per day", "Maximum day", "Lowest day"], 
            "Value": [f'{metrics["total_kwh"]:.2f} kWh', f'{metrics["daily_avg_kwh"]:.2f} kWh', f'{metrics["peak_usage_kwh"]:.2f} kWh', f'{metrics["lowest_usage_kwh"]:.2f} kWh']
        })
        st.dataframe(stats_table, hide_index=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ----------------- ANOMALY DETECTION TAB -----------------
elif page == "Anomaly Detection":
    result = detect_anomalies(daily)
    anomalies = result[result["is_anomaly"]]
    
    c1, c2, c3 = st.columns(3, gap="small")
    with c1: metric_card("Unusual days", str(len(anomalies)), "", "Potential outliers", "⚠️")
    with c2: metric_card("Normal days", str(len(result)-len(anomalies)), "", "Within expected range", "✓")
    with c3: metric_card("Detection method", "Isolation Forest", "", "Unsupervised ML Engine", "🧠")
    
    st.markdown('<div class="panel"><b>Anomaly Monitoring Chart</b>', unsafe_allow_html=True)
    fig_anom = px.scatter(result, x='timestamp', y='consumption_kwh', color='is_anomaly', 
                          color_discrete_map={True: 'red', False: 'blue'},
                          title="Daily Usage Anomaly Inspection")
    st.plotly_chart(fig_anom, use_container_width=True, config={"displayModeBar": False})
    
    if anomalies.empty:
        st.success("No unusual daily readings were flagged in this dataset.")
    else:
        st.warning(f"{len(anomalies)} potentially unusual day(s) detected.")
        display_cols = [c for c in ["timestamp", "consumption_kwh", "z_score", "anomaly_severity"] if c in anomalies.columns]
        st.dataframe(anomalies[display_cols], use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ----------------- PREDICTIONS TAB -----------------
elif page == "Predictions":
    horizon = st.slider("Forecast horizon (days)", 3, 14, 5)
    try:
        forecast_df, metrics_eval = train_and_forecast(daily, forecast_days=horizon)
        st.markdown('<div class="panel"><b>Energy Demand Forecast</b>', unsafe_allow_html=True)
        st.caption(f"🤖 Random Forest Model Performance: MAE = {metrics_eval['mae']} kWh | RMSE = {metrics_eval['rmse']} kWh")
        
        fig_fc = px.bar(forecast_df, x='timestamp', y='predicted_kwh', title=f"Predicted Usage for Next {horizon} Days")
        st.plotly_chart(fig_fc, use_container_width=True, config={"displayModeBar": False})
        
        st.dataframe(forecast_df.rename(columns={"timestamp":"Forecast Date", "predicted_kwh":"Predicted Consumption (kWh)"}), use_container_width=True, hide_index=True)
        st.download_button("Download forecast CSV", forecast_df.to_csv(index=False).encode("utf-8"), "ecosense_forecast.csv", "text/csv")
        st.markdown('</div>', unsafe_allow_html=True)
    except Exception as err:
        st.error(f"Prediction model requires at least 7 historical days. ({err})")

# ----------------- RECOMMENDATIONS TAB -----------------
elif page == "Recommendations":
    anom_df = detect_anomalies(daily)
    score, recs = calculate_energy_score_and_recs(daily, anom_df)
    
    st.markdown(f'<div class="panel"><h2>Energy Efficiency Score: {score}/100</h2><p style="color:#6c757d;">Actionable advice based on patterns detected in your uploaded dataset.</p><hr>', unsafe_allow_html=True)
    for rec in recs:
        icon = "⚠️" if rec['type'] == 'warning' else ("✅" if rec['type'] == 'success' else "💡")
        st.markdown(
            f"""
            <div style="background:#f8f9fa; padding:15px; border-radius:8px; margin-bottom:10px; border-left:4px solid #0d6efd;">
                <div style="font-size:1.1rem; font-weight:bold;">{icon} {rec['title']}</div>
                <div style="color:#495057; margin-top:5px;">{rec['body']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.8rem; color:#6c757d; margin-top:15px;">Disclaimer: EcoSense recommendations are data-driven prompts. They do not identify a specific appliance unless appliance-level readings are supplied.</div>', unsafe_allow_html=True)

st.markdown('<hr><div style="text-align:center; color:#6c757d; font-size:0.85rem;">🌿 EcoSense <span>· Understand Your Energy. Detect Waste. Save Smarter.</span></div>', unsafe_allow_html=True)