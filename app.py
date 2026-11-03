import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# Core Modules Import
from modules.data_cleaner import (
    clean_energy_data,
    aggregate_daily,
    compute_summary_analytics,
)
from modules.anomaly_detection import detect_anomalies
from modules.prediction import train_and_forecast
from modules.recommendations import calculate_energy_score_and_recs
from modules.cost_estimator import estimate_electricity_cost

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="EcoSense | Smart Energy Analyzer",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------
# THEME STATE INITIALIZATION
# --------------------------------------------------

<<<<<<< HEAD
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# Dynamic CSS Theme Engine (No external assets folder needed)
if st.session_state.theme == "Dark":
    theme_css = """
    <style>
        .stApp { background-color: #0f172a; color: #f8fafc; }
        [data-testid="stSidebar"] { background-color: #1e293b !important; border-right: 1px solid #334155; }
        h1, h2, h3, h4, p, label, span, div { color: #f8fafc !important; }
        .main-title { font-size: 34px; font-weight: 800; color: #34d399 !important; margin-bottom: 2px; }
        .subtitle { color: #94a3b8 !important; margin-bottom: 20px; font-size: 15px; }
        .metric-card { background: #1e293b; padding: 20px; border: 1px solid #334155; border-radius: 14px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .metric-label { color: #94a3b8 !important; font-size: 13px; font-weight: 600; text-transform: uppercase; }
        .metric-value { color: #34d399 !important; font-size: 28px; font-weight: 800; margin-top: 6px; }
        .metric-note { color: #64748b !important; font-size: 12px; margin-top: 4px; }
        .summary-box { background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 20px; }
        .stNumberInput input { background-color: #334155 !important; color: #ffffff !important; }
    </style>
    """
    plotly_bg = "#1e293b"
    plotly_paper = "#1e293b"
    plotly_text = "#f8fafc"
    accent_green = "#34d399"
else:
    theme_css = """
    <style>
        .stApp { background-color: #f8fafc; color: #0f172a; }
        [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #e2e8f0; }
        .main-title { font-size: 34px; font-weight: 800; color: #059669 !important; margin-bottom: 2px; }
        .subtitle { color: #64748b !important; margin-bottom: 20px; font-size: 15px; }
        .metric-card { background: #ffffff; padding: 20px; border: 1px solid #e2e8f0; border-radius: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
        .metric-label { color: #64748b !important; font-size: 13px; font-weight: 600; text-transform: uppercase; }
        .metric-value { color: #059669 !important; font-size: 28px; font-weight: 800; margin-top: 6px; }
        .metric-note { color: #94a3b8 !important; font-size: 12px; margin-top: 4px; }
        .summary-box { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; }
    </style>
    """
    plotly_bg = "#ffffff"
    plotly_paper = "#ffffff"
    plotly_text = "#0f172a"
    accent_green = "#059669"
=======
st.markdown("""
<style>
    :root {
        color-scheme: light;
    }

    /* Main page and sidebar */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: #F7FAF7 !important;
        color: #17251B !important;
    }

    [data-testid="stHeader"] {
        background: #F7FAF7 !important;
    }

    [data-testid="stSidebar"] {
        background: #EAF4EB !important;
    }

    /* Main text */
    .stApp,
    .stApp p,
    .stApp label,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp li,
    .stApp [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span {
        color: #17251B;
    }

    .stApp [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color: #526B59 !important;
    }

    .main-title {
        font-size: 34px;
        font-weight: 800;
        color: #176B3A !important;
        margin-bottom: 4px;
    }

    .subtitle {
        color: #526B59 !important;
        margin-bottom: 25px;
    }

    /* Metric and content cards */
    .metric-card {
        background: #FFFFFF;
        padding: 20px;
        border: 1px solid #DCE9DE;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(20, 70, 35, 0.06);
    }

    .metric-label {
        color: #526B59 !important;
        font-size: 14px;
    }

    .metric-value {
        color: #176B3A !important;
        font-size: 27px;
        font-weight: 800;
        margin-top: 8px;
    }

    .metric-note {
        color: #647568 !important;
        font-size: 12px;
        margin-top: 5px;
    }

    .section-card {
        background: #FFFFFF;
        border: 1px solid #DCE9DE;
        padding: 20px;
        border-radius: 14px;
        margin-bottom: 18px;
    }

    .section-title {
        color: #176B3A !important;
        font-size: 19px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .recommendation {
        background: #EFF7F0;
        border-left: 4px solid #269653;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
    }

    .footer {
        text-align: center;
        color: #526B59 !important;
        padding: 25px 0 10px;
        font-size: 13px;
    }

    /* File uploader: drop area, instructions, icons and browse button */
    [data-testid="stFileUploader"],
    [data-testid="stFileUploader"] > section,
    [data-testid="stFileUploader"] section {
        color: #17251B !important;
    }

    [data-testid="stFileUploader"] section {
        background: #FFFFFF !important;
        border: 2px dashed #198747 !important;
        border-radius: 12px !important;
        padding: 18px !important;
    }

    [data-testid="stFileUploader"] section *,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] p {
        color: #17251B !important;
        opacity: 1 !important;
    }

    [data-testid="stFileUploader"] svg {
        color: #198747 !important;
        fill: #198747 !important;
    }

    [data-testid="stFileUploader"] button {
        background: #EAF4EB !important;
        color: #176B3A !important;
        border: 1px solid #198747 !important;
    }

    [data-testid="stFileUploader"] button * {
        color: #176B3A !important;
    }

    /* All Streamlit buttons */
    .stButton > button,
    .stDownloadButton > button,
    [data-testid="stFileUploader"] button {
        background: #198747 !important;
        color: #FFFFFF !important;
        border: 1px solid #198747 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    .stButton > button *,
    .stDownloadButton > button * {
        color: #FFFFFF !important;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        background: #126B36 !important;
        border-color: #126B36 !important;
    }

    /* Text input, number input and text area */
    [data-testid="stTextInput"] input,
    [data-testid="stNumberInput"] input,
    [data-testid="stTextArea"] textarea {
        background: #FFFFFF !important;
        color: #17251B !important;
        border: 1px solid #B9CEBD !important;
        -webkit-text-fill-color: #17251B !important;
    }

    [data-testid="stTextInput"] input::placeholder,
    [data-testid="stTextArea"] textarea::placeholder {
        color: #718176 !important;
        opacity: 1 !important;
    }

    [data-testid="stNumberInput"] button {
        background: #EAF4EB !important;
        color: #176B3A !important;
        border: 1px solid #B9CEBD !important;
    }

    [data-testid="stNumberInput"] button svg {
        color: #176B3A !important;
        fill: #176B3A !important;
    }

    /* Select boxes and dropdown menus */
    [data-baseweb="select"] > div,
    [data-baseweb="popover"],
    [role="listbox"],
    [role="option"] {
        background: #FFFFFF !important;
        color: #17251B !important;
    }

    [data-baseweb="select"] *,
    [role="option"] * {
        color: #17251B !important;
    }

    /* Radio buttons and sidebar navigation */
    [data-testid="stRadio"] label,
    [data-testid="stRadio"] label p {
        color: #17251B !important;
    }

    [data-testid="stRadio"] svg {
        color: #198747 !important;
        fill: #198747 !important;
    }

    [data-testid="stSidebar"] svg {
        color: #198747 !important;
    }

    /* Data tables */
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        background: #FFFFFF !important;
        color: #17251B !important;
    }

    /* Alerts and status messages */
    [data-testid="stAlert"] {
        color: #17251B !important;
    }

    [data-testid="stAlert"] p {
        color: #17251B !important;
    }

    /* Slider labels and values */
    [data-testid="stSlider"] label,
    [data-testid="stSlider"] [data-testid="stMarkdownContainer"] {
        color: #17251B !important;
    }

    /* Keep icons visible */
    .stApp svg {
        opacity: 1;
    }

    /* Progress bar */
    [data-testid="stProgressBar"] > div > div {
        background: #198747 !important;
    }
</style>
""", unsafe_allow_html=True)
>>>>>>> 13070a8 (Improve EcoSense UI with accessible light theme)

st.markdown(theme_css, unsafe_allow_html=True)

# --------------------------------------------------
# DATA ENGINE HELPERS
# --------------------------------------------------

BASE_DIR = Path(__file__).parent
SAMPLE_FILE = BASE_DIR / "sample_data" / "normal_usage.csv"

def prepare_data(raw_df):
    cleaned = clean_energy_data(raw_df)
    if cleaned.empty:
        raise ValueError("The dataset has no valid records.")
    daily = aggregate_daily(cleaned)
    if daily.empty:
        raise ValueError("Unable to create daily energy summaries.")
    return cleaned, daily

def load_sample_data():
    if not SAMPLE_FILE.exists():
        # Built-in synthetic fallback if file missing
        dates = pd.date_range(start="2026-10-01", periods=30, freq="D")
        np.random.seed(42)
        vals = np.random.uniform(8.0, 12.0, size=30)
        vals[4] = 24.5  # Artificial spike
        vals[17] = 28.2 # Artificial spike
        raw = pd.DataFrame({"timestamp": dates, "consumption_kwh": np.round(vals, 2)})
    else:
        raw = pd.read_csv(SAMPLE_FILE)
    return prepare_data(raw)

if "energy_data" not in st.session_state:
    try:
        cleaned, daily = load_sample_data()
        st.session_state.energy_data = cleaned
        st.session_state.daily_data = daily
        st.session_state.source_name = "Normal usage sample dataset"
    except Exception as error:
        st.error(f"Could not load sample data: {error}")
        st.stop()

df = st.session_state.energy_data.copy()
daily = st.session_state.daily_data.copy()
tariff = st.session_state.get("tariff", 7.0)

summary = compute_summary_analytics(daily)
bill = estimate_electricity_cost(summary.get("total_kwh", 0), rate_per_kwh=tariff)

def metric_card(label, value, note=""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# --------------------------------------------------
# SIDEBAR NAVIGATION & THEME TOGGLE
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 🌿 EcoSense")
    st.caption("SMART ENERGY INTELLIGENCE")
    st.divider()

    # Theme Selector
    theme_choice = st.radio("🎨 App Theme", ["Light", "Dark"], horizontal=True)
    if theme_choice != st.session_state.theme:
        st.session_state.theme = theme_choice
        st.rerun()

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Upload Data",
            "Analytics",
            "Anomaly Detection",
            "Predictions",
            "Recommendations",
        ],
    )

    st.divider()

    tariff_input = st.number_input(
        "Electricity rate (₹/kWh)",
        min_value=0.0,
        max_value=100.0,
        value=float(st.session_state.get("tariff", 7.0)),
        step=0.5,
    )
    st.session_state.tariff = tariff_input

    st.caption("Current Dataset:")
    st.info(st.session_state.source_name)

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown('<div class="main-title">🌿 EcoSense</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Smart Energy Consumption Analyzer</div>', unsafe_allow_html=True)

# --------------------------------------------------
# TAB 1: OVERVIEW
# --------------------------------------------------

if page == "Overview":
    st.header("Energy Overview")
    st.caption("A high-level snapshot of your household electricity performance.")

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Total Consumption", f'{summary["total_kwh"]:,.2f} kWh', "Total recorded usage")
    with c2: metric_card("Daily Average", f'{summary["daily_avg_kwh"]:,.2f} kWh', "Average daily consumption")
    with c3: metric_card("Peak Consumption", f'{summary["peak_usage_kwh"]:,.2f} kWh', f"Peak on {summary['peak_date']}")
    with c4: metric_card("Estimated Bill", f'₹{bill["total_estimated_cost"]:,.2f}', f"Rate: ₹{tariff_input:.2f}/kWh")

    st.divider()

    left, right = st.columns([1.6, 1])

    with left:
        st.subheader("Daily Energy Consumption Trend")
        fig = px.area(
            daily,
            x="timestamp",
            y="consumption_kwh",
            markers=True,
            labels={"timestamp": "Date", "consumption_kwh": "Consumption (kWh)"},
        )
        fig.update_traces(line_color=accent_green, fillcolor="rgba(16, 185, 129, 0.15)")
        fig.update_layout(
            plot_bgcolor=plotly_bg,
            paper_bgcolor=plotly_paper,
            font_color=plotly_text,
            margin=dict(l=10, r=10, t=10, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Bill & Usage Breakdown")
        st.markdown(
            f"""
            <div class="summary-box">
                <p><b>Lowest Usage:</b> {summary['lowest_usage_kwh']:.2f} kWh</p>
                <p><b>Lowest Usage Date:</b> {summary['lowest_date']}</p>
                <p><b>Recorded Days:</b> {len(daily)}</p>
                <hr>
                <p><b>Energy Charge:</b> ₹{bill['energy_charge']:,.2f}</p>
                <p><b>Fixed Grid Charge:</b> ₹{bill['fixed_charge']:,.2f}</p>
                <p><b>Tax Charge (9%):</b> ₹{bill['tax_charge']:,.2f}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# --------------------------------------------------
# TAB 2: UPLOAD DATA
# --------------------------------------------------

elif page == "Upload Data":
    st.header("Upload Energy Dataset")
    st.write("Upload a custom CSV file containing `timestamp` and `consumption_kwh` columns.")

    uploaded_file = st.file_uploader("Choose your CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            raw = pd.read_csv(uploaded_file)
            cleaned, new_daily = prepare_data(raw)
            st.success(f"Successfully processed {len(cleaned):,} rows.")
            st.dataframe(cleaned.head(10), use_container_width=True, hide_index=True)

            if st.button("Use Uploaded Dataset", type="primary"):
                st.session_state.energy_data = cleaned
                st.session_state.daily_data = new_daily
                st.session_state.source_name = uploaded_file.name
                st.success("Dataset activated!")
                st.rerun()
        except Exception as error:
            st.error(f"Unable to process CSV file: {error}")

    st.divider()
    st.subheader("Active Dataset Preview")
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.download_button(
            "Download Active Dataset CSV",
            df.to_csv(index=False).encode("utf-8"),
            "ecosense_data.csv",
            "text/csv",
        )
    with col2:
        if st.button("Restore Sample Dataset"):
            cleaned, new_daily = load_sample_data()
            st.session_state.energy_data = cleaned
            st.session_state.daily_data = new_daily
            st.session_state.source_name = "Normal usage sample dataset"
            st.success("Sample dataset restored.")
            st.rerun()

# --------------------------------------------------
# TAB 3: ANALYTICS
# --------------------------------------------------

elif page == "Analytics":
    st.header("Energy Analytics")

    period = st.selectbox("Select analysis period", ["Daily", "Weekly", "Monthly"])

    if period == "Daily":
        chart_data = daily.copy()
        title = "Daily Consumption"
    elif period == "Weekly":
        chart_data = df.set_index("timestamp").resample("W")["consumption_kwh"].sum().reset_index()
        title = "Weekly Consumption"
    else:
        chart_data = df.set_index("timestamp").resample("MS")["consumption_kwh"].sum().reset_index()
        title = "Monthly Consumption"

    fig = px.bar(
        chart_data,
        x="timestamp",
        y="consumption_kwh",
        title=title,
        labels={"timestamp": "Date", "consumption_kwh": "Consumption (kWh)"},
    )
    fig.update_traces(marker_color=accent_green)
    fig.update_layout(plot_bgcolor=plotly_bg, paper_bgcolor=plotly_paper, font_color=plotly_text)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Average Consumption by Weekday")
    weekday_data = df.groupby("day_of_week")["consumption_kwh"].mean().reindex(range(7)).reset_index()
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_data["weekday"] = weekday_data["day_of_week"].map(dict(enumerate(weekday_names)))

    fig_weekday = px.bar(
        weekday_data,
        x="weekday",
        y="consumption_kwh",
        labels={"weekday": "Day", "consumption_kwh": "Avg kWh"},
    )
    fig_weekday.update_traces(marker_color=accent_green)
    fig_weekday.update_layout(plot_bgcolor=plotly_bg, paper_bgcolor=plotly_paper, font_color=plotly_text)
    st.plotly_chart(fig_weekday, use_container_width=True)

# --------------------------------------------------
# TAB 4: ANOMALY DETECTION
# --------------------------------------------------

elif page == "Anomaly Detection":
    st.header("Anomaly Detection")
    st.caption("Isolation Forest detects readings that deviate significantly from baseline behavior.")

    try:
        anom_df = detect_anomalies(daily)
        anomalies = anom_df[anom_df["is_anomaly"]]

        c1, c2, c3 = st.columns(3)
        with c1: metric_card("Unusual Readings", str(len(anomalies)), "Potential anomalies")
        with c2: metric_card("Normal Readings", str(len(anom_df) - len(anomalies)), "Within expected range")
        with c3: metric_card("Detection Engine", "Isolation Forest", "Unsupervised ML Model")

        fig = px.scatter(
            anom_df,
            x="timestamp",
            y="consumption_kwh",
            color="is_anomaly",
            color_discrete_map={True: "#ef4444", False: accent_green},
            labels={"timestamp": "Date", "consumption_kwh": "Consumption (kWh)", "is_anomaly": "Anomaly"},
        )
        fig.update_layout(plot_bgcolor=plotly_bg, paper_bgcolor=plotly_paper, font_color=plotly_text)
        st.plotly_chart(fig, use_container_width=True)

        if not anomalies.empty:
            st.warning(f"Detected {len(anomalies)} unusual daily spike(s).")
            display_cols = [c for c in ["timestamp", "consumption_kwh", "z_score", "anomaly_severity"] if c in anomalies.columns]
            st.dataframe(anomalies[display_cols], use_container_width=True, hide_index=True)
        else:
            st.success("No abnormal energy spikes detected in this dataset.")

    except Exception as error:
        st.error(f"Anomaly detection failed: {error}")

# --------------------------------------------------
# TAB 5: PREDICTIONS
# --------------------------------------------------

elif page == "Predictions":
    st.header("Energy Consumption Forecast")
    horizon_days = st.slider("Forecast duration (days)", min_value=3, max_value=14, value=5)

    try:
        forecast_df, eval_metrics = train_and_forecast(daily, forecast_days=horizon_days)

        c1, c2 = st.columns(2)
        with c1: metric_card("Forecasted Days", f"{horizon_days} Days", "Prediction horizon")
        with c2: metric_card("Validation Error (MAE)", f"{eval_metrics['mae']} kWh", "Random Forest accuracy metric")

        fig_fc = px.bar(
            forecast_df,
            x="timestamp",
            y="predicted_kwh",
            title=f"Predicted kWh for Next {horizon_days} Days",
            labels={"timestamp": "Date", "predicted_kwh": "Predicted kWh"},
        )
        fig_fc.update_traces(marker_color="#f59e0b")
        fig_fc.update_layout(plot_bgcolor=plotly_bg, paper_bgcolor=plotly_paper, font_color=plotly_text)
        st.plotly_chart(fig_fc, use_container_width=True)

        st.dataframe(forecast_df, use_container_width=True, hide_index=True)

    except Exception as error:
        st.error(f"Forecasting engine unavailable: {error}")

# --------------------------------------------------
# TAB 6: RECOMMENDATIONS
# --------------------------------------------------

elif page == "Recommendations":
    st.header("Smart Energy Recommendations")

    try:
        anom_df = detect_anomalies(daily)
        score, recs = calculate_energy_score_and_recs(daily, anom_df)

        c1, c2 = st.columns([1, 2])
        with c1:
            st.metric("Efficiency Rating", f"{score}/100")
            st.progress(score / 100)
        with c2:
            if score >= 80:
                st.success("Excellent energy efficiency performance!")
            elif score >= 50:
                st.warning("Moderate energy efficiency. Follow tips below to optimize.")
            else:
                st.error("High energy waste detected! Review spikes immediately.")

        st.divider()
        st.subheader("Actionable Recommendations")

        for r in recs:
            st.info(f"**{r['title']}**: {r['body']}")

    except Exception as error:
        st.error(f"Unable to generate recommendations: {error}")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown('<hr><div style="text-align:center; color:#94a3b8; font-size:13px;">🌿 EcoSense | Understand Your Energy. Detect Waste. Save Smarter.</div>', unsafe_allow_html=True)