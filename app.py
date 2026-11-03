import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path

from modules.data_loader import load_and_validate, make_sample_data
from modules.energy_analysis import calculate_metrics, daily_summary, monthly_summary
from modules.anomaly_detection import detect_anomalies
from modules.prediction import forecast_consumption
from modules.recommendations import generate_recommendations
from modules.visualizations import consumption_chart, weekday_chart, anomaly_chart, forecast_chart

st.set_page_config(
    page_title="EcoSense | Smart Energy Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CSS_PATH = Path(__file__).parent / "assets" / "style.css"
st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)

if "energy_df" not in st.session_state:
    st.session_state.energy_df = make_sample_data()
if "source_name" not in st.session_state:
    st.session_state.source_name = "Built-in demonstration dataset"

def fmt_num(value, digits=1):
    return f"{value:,.{digits}f}"

def metric_card(label, value, suffix="", note="", icon="⚡"):
    st.markdown(
        f"""
        <div class="metric-card">
          <div class="metric-top"><span>{icon}</span><span class="metric-label">{label}</span></div>
          <div class="metric-value">{value}<small>{suffix}</small></div>
          <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

df = st.session_state.energy_df.copy()
metrics = calculate_metrics(df, st.session_state.get("tariff", 5.0))
daily = daily_summary(df)

st.markdown(
    """
    <div class="app-header">
      <div class="brand-wrap">
        <div class="brand-mark">🌿</div>
        <div><div class="brand-name">EcoSense</div><div class="brand-sub">SMART ENERGY INTELLIGENCE</div></div>
      </div>
      <div class="header-status"><span class="status-dot"></span> DEMO SYSTEM ONLINE</div>
    </div>
    """,
    unsafe_allow_html=True,
)

nav_items = ["Overview", "Upload Data", "Analytics", "Anomaly Detection", "Predictions", "Recommendations"]
page = st.radio("Navigation", nav_items, horizontal=True, label_visibility="collapsed", key="main_navigation")
st.markdown('<div class="thin-rule"></div>', unsafe_allow_html=True)

# Shared page intro
page_descriptions = {
    "Overview": "A clear snapshot of your household energy performance.",
    "Upload Data": "Import your electricity readings and validate the dataset.",
    "Analytics": "Explore consumption patterns across days and months.",
    "Anomaly Detection": "Find unusually high or low usage patterns in your readings.",
    "Predictions": "Estimate upcoming energy demand from historical consumption.",
    "Recommendations": "Turn your energy data into practical next steps.",
}
st.markdown(f'<div class="page-kicker">ENERGY WORKSPACE / {page.upper()}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="page-title">{page}</div><div class="page-description">{page_descriptions[page]}</div>', unsafe_allow_html=True)

if page == "Overview":
    st.markdown('<div class="section-heading">Your energy at a glance <span class="soft-pill">DEMO DATA</span></div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4, gap="small")
    with c1: metric_card("Total consumption", fmt_num(metrics["total"]), "kWh", "Across selected dataset", "⚡")
    with c2: metric_card("Daily average", fmt_num(metrics["average"]), "kWh", "Average per recorded day", "📊")
    with c3: metric_card("Highest usage", fmt_num(metrics["maximum"]), "kWh", metrics["max_date"], "↗")
    with c4: metric_card("Estimated bill", f"₹{metrics['estimated_cost']:,.0f}", "", f"At ₹{metrics['tariff']:.2f} per kWh", "₹")

    left, right = st.columns([1.65, 1], gap="small")
    with left:
        st.markdown('<div class="panel"><div class="panel-title">Consumption trend</div><div class="panel-subtitle">Daily electricity usage · kWh</div>', unsafe_allow_html=True)
        st.plotly_chart(consumption_chart(daily), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><div class="panel-title">Usage summary</div><div class="panel-subtitle">Key readings from your data</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary-line"><span>Lowest daily usage</span><b>{metrics["minimum"]:.2f} kWh</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary-line"><span>Recorded days</span><b>{metrics["days"]}</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary-line"><span>Estimated monthly cost</span><b>₹{metrics["estimated_cost"]:,.0f}</b></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary-line"><span>Data source</span><b class="source-name">{st.session_state.source_name}</b></div>', unsafe_allow_html=True)
        st.markdown('<div class="insight-box"><b>💡 Eco insight</b><p>Compare similar days and investigate repeated spikes before assuming they indicate waste.</p></div></div>', unsafe_allow_html=True)
    st.caption("All values are calculated from the currently loaded dataset. The built-in data is illustrative.")

elif page == "Upload Data":
    st.markdown('<div class="panel upload-panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">Upload electricity readings</div><div class="panel-subtitle">CSV should contain a timestamp/date column and a consumption column.</div>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Choose a CSV file", type=["csv"], help="Accepted columns: timestamp and consumption_kwh. Common date/usage column names are also detected.")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        tariff = st.number_input("Electricity tariff (₹ per kWh)", min_value=0.0, max_value=100.0, value=5.0, step=0.25)
    with col_b:
        st.markdown('<div class="format-hint"><b>Expected format</b><br><code>timestamp,consumption_kwh</code><br><code>2026-10-01 00:00,0.32</code></div>', unsafe_allow_html=True)
    if uploaded is not None:
        try:
            candidate, report = load_and_validate(uploaded)
            st.success(f"Successfully read {len(candidate):,} valid records.")
            st.info(f"Date range: {candidate['timestamp'].min():%d %b %Y} – {candidate['timestamp'].max():%d %b %Y}")
            st.dataframe(candidate.head(12), use_container_width=True, hide_index=True)
            if st.button("Use this dataset", type="primary", use_container_width=True):
                st.session_state.energy_df = candidate
                st.session_state.source_name = uploaded.name
                st.session_state.tariff = tariff
                st.success("Dataset loaded. Open Overview or Analytics to explore it.")
                st.rerun()
            if report:
                st.warning("Data notes: " + " · ".join(report))
        except Exception as exc:
            st.error(f"Could not load this file: {exc}")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-title">Dataset preview</div><div class="panel-subtitle">Currently active data</div>', unsafe_allow_html=True)
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)
    st.download_button("Download active dataset", df.to_csv(index=False).encode("utf-8"), "ecosense_data.csv", "text/csv")
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("Restore demonstration dataset"):
        st.session_state.energy_df = make_sample_data()
        st.session_state.source_name = "Built-in demonstration dataset"
        st.rerun()

elif page == "Analytics":
    d1, d2 = st.columns([1, 1])
    with d1:
        period = st.selectbox("Aggregation", ["Daily", "Weekly", "Monthly"])
    with d2:
        st.markdown('<div class="mini-note">Charts update from the active dataset.</div>', unsafe_allow_html=True)
    if period == "Daily":
        chart_data = daily
        label = "Daily consumption"
    elif period == "Weekly":
        chart_data = df.set_index("timestamp").resample("W")["consumption_kwh"].sum().reset_index()
        label = "Weekly consumption"
    else:
        chart_data = monthly_summary(df)
        label = "Monthly consumption"
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(f'<div class="panel-title">{label}</div><div class="panel-subtitle">Energy consumed in kWh</div>', unsafe_allow_html=True)
    st.plotly_chart(consumption_chart(chart_data, title=label), use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)
    left, right = st.columns(2, gap="small")
    with left:
        st.markdown('<div class="panel"><div class="panel-title">Average usage by weekday</div>', unsafe_allow_html=True)
        st.plotly_chart(weekday_chart(df), use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><div class="panel-title">Consumption statistics</div>', unsafe_allow_html=True)
        stats = pd.DataFrame({"Metric": ["Total", "Average per day", "Maximum day", "Minimum day"], "Value": [f'{metrics["total"]:.2f} kWh', f'{metrics["average"]:.2f} kWh', f'{metrics["maximum"]:.2f} kWh', f'{metrics["minimum"]:.2f} kWh']})
        st.dataframe(stats, hide_index=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

elif page == "Anomaly Detection":
    result = detect_anomalies(daily)
    anomalies = result[result["is_anomaly"]]
    c1, c2, c3 = st.columns(3, gap="small")
    with c1: metric_card("Unusual days", str(len(anomalies)), "", "Potential outliers", "⚠️")
    with c2: metric_card("Normal days", str(len(result)-len(anomalies)), "", "Within expected range", "✓")
    with c3: metric_card("Detection method", "I-Forest", "", "Unsupervised ML", "🧠")
    st.markdown('<div class="panel"><div class="panel-title">Anomaly monitoring</div><div class="panel-subtitle">Isolation Forest highlights observations that differ from the overall pattern.</div>', unsafe_allow_html=True)
    st.plotly_chart(anomaly_chart(result), use_container_width=True, config={"displayModeBar": False})
    if anomalies.empty:
        st.success("No unusual daily readings were flagged in this dataset.")
    else:
        st.warning(f"{len(anomalies)} potentially unusual day(s) detected. An anomaly is not proof of energy wastage.")
        st.dataframe(anomalies[["timestamp", "consumption_kwh", "is_anomaly"]].rename(columns={"timestamp":"Date", "consumption_kwh":"Consumption (kWh)", "is_anomaly":"Flagged"}), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Predictions":
    horizon = st.slider("Forecast horizon (days)", 3, 14, 7)
    forecast, model_note = forecast_consumption(daily, horizon)
    st.markdown('<div class="panel"><div class="panel-title">Energy demand forecast</div><div class="panel-subtitle">Historical usage and estimated future consumption</div>', unsafe_allow_html=True)
    st.plotly_chart(forecast_chart(daily, forecast), use_container_width=True, config={"displayModeBar": False})
    st.markdown(f'<div class="insight-box"><b>Forecast method</b><p>{model_note}</p></div>', unsafe_allow_html=True)
    st.dataframe(forecast.rename(columns={"timestamp":"Forecast date", "predicted_kwh":"Predicted consumption (kWh)"}), use_container_width=True, hide_index=True)
    st.download_button("Download forecast CSV", forecast.to_csv(index=False).encode("utf-8"), "ecosense_forecast.csv", "text/csv")
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption("Forecasts are estimates, not guaranteed future readings. More historical data generally improves reliability.")

elif page == "Recommendations":
    recs = generate_recommendations(daily)
    st.markdown('<div class="panel"><div class="panel-title">Your energy action plan</div><div class="panel-subtitle">Suggestions generated from patterns in the uploaded readings.</div>', unsafe_allow_html=True)
    for rec in recs:
        st.markdown(f'<div class="recommendation"><div class="rec-icon">{rec["icon"]}</div><div><b>{rec["title"]}</b><p>{rec["detail"]}</p><span>{rec["priority"]}</span></div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="disclaimer">EcoSense recommendations are data-driven prompts. They do not identify a specific appliance unless appliance-level readings are supplied.</div>', unsafe_allow_html=True)

st.markdown('<div class="footer">🌿 EcoSense <span>Understand Your Energy. Detect Waste. Save Smarter.</span></div>', unsafe_allow_html=True)
