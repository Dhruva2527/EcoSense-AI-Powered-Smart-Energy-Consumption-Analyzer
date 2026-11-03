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
# THEME STATE INITIALIZATION & DYNAMIC STYLING
# --------------------------------------------------

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

if st.session_state.theme == "Dark":
    theme_css = """
    <style>
        .stApp { background-color: #0f172a !important; color: #f8fafc !important; }
        [data-testid="stSidebar"] { background-color: #1e293b !important; border-right: 1px solid #334155; }
        [data-testid="stSidebar"] * { color: #f8fafc !important; }
        
        .main-title { font-size: 34px; font-weight: 800; color: #34d399 !important; margin-bottom: 2px; }
        .subtitle { color: #94a3b8 !important; margin-bottom: 20px; font-size: 15px; }
        
        .metric-card { 
            background: #1e293b; 
            padding: 20px; 
            border: 1px solid #334155; 
            border-top: 4px solid #34d399;
            border-radius: 14px; 
        }
        .metric-label { color: #94a3b8 !important; font-size: 13px; font-weight: 600; text-transform: uppercase; }
        .metric-value { color: #34d399 !important; font-size: 28px; font-weight: 800; margin-top: 6px; }
        .metric-note { color: #64748b !important; font-size: 12px; margin-top: 4px; }
        
        .summary-box { background: #1e293b; border: 1px solid #334155; border-radius: 14px; padding: 20px; }
        .summary-box * { color: #f8fafc !important; }
        
        .dataset-badge { background-color: #283447; color: #34d399 !important; padding: 12px; border-radius: 8px; border-left: 4px solid #34d399; font-weight: 600; }
        
        div[data-testid="stAlert"] * { color: #fef08a !important; }

        /* DARK MODE INPUT FIX: Force dark background & bright white text on selectboxes, inputs, and buttons */
        div[data-baseweb="select"] > div { 
            background-color: #334155 !important; 
            border: 1px solid #475569 !important; 
            color: #ffffff !important; 
        }
        div[data-baseweb="select"] * { 
            color: #ffffff !important; 
            fill: #ffffff !important; 
        }

        div[data-baseweb="input"] { 
            background-color: #334155 !important; 
            border: 1px solid #475569 !important; 
        }
        div[data-baseweb="input"] input { 
            background-color: #334155 !important; 
            color: #ffffff !important; 
        }

        [data-testid="stNumberInput"] button { 
            background-color: #475569 !important; 
            border-color: #64748b !important; 
        }
        [data-testid="stNumberInput"] button * { 
            color: #ffffff !important; 
            fill: #ffffff !important; 
            stroke: #ffffff !important; 
        }

        .stButton > button { 
            background-color: #334155 !important; 
            color: #ffffff !important; 
            border: 1px solid #475569 !important; 
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
    </style>
    """
    plotly_bg = "#1e293b"
    plotly_paper = "#1e293b"
    plotly_text = "#f8fafc"
    plotly_axis = "#cbd5e1"
    plotly_grid = "#334155"
    accent_green = "#34d399"
else:
    theme_css = """
    <style>
        .stAppHeader { background-color: #f1f5f9 !important; }
        .stApp { background-color: #f1f5f9 !important; color: #0f172a !important; }
        
        [data-testid="stSidebar"] { background-color: #ffffff !important; border-right: 1px solid #cbd5e1; }
        [data-testid="stSidebar"] * { color: #0f172a !important; }
        [data-testid="stSidebar"] .stCaption { color: #64748b !important; }

        .main-title { font-size: 34px; font-weight: 800; color: #059669 !important; margin-bottom: 2px; }
        .subtitle { color: #64748b !important; margin-bottom: 20px; font-size: 15px; }
        
        .metric-card { 
            background: #ffffff; 
            padding: 20px; 
            border: 1px solid #e2e8f0; 
            border-top: 4px solid #059669;
            border-radius: 14px; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        }
        .metric-label { color: #64748b !important; font-size: 13px; font-weight: 600; text-transform: uppercase; }
        .metric-value { color: #059669 !important; font-size: 28px; font-weight: 800; margin-top: 6px; }
        .metric-note { color: #94a3b8 !important; font-size: 12px; margin-top: 4px; }
        
        .summary-box { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px; }
        .summary-box * { color: #0f172a !important; }

        .dataset-badge { background-color: #e2e8f0; color: #047857 !important; padding: 12px; border-radius: 8px; border-left: 4px solid #059669; font-weight: 600; }
        
        div[data-testid="stAlert"] * { color: #854d0e !important; }

        /* LIGHT MODE INPUT FIX: Keep white background and clear dark text */
        div[data-baseweb="select"] > div { 
            background-color: #ffffff !important; 
            border: 1px solid #cbd5e1 !important; 
            color: #0f172a !important; 
        }
        div[data-baseweb="select"] * { color: #0f172a !important; }
        
        div[data-baseweb="input"] { 
            background-color: #ffffff !important; 
            border: 1px solid #cbd5e1 !important; 
        }
        div[data-baseweb="input"] input { 
            background-color: #ffffff !important; 
            color: #0f172a !important; 
        }

        [data-testid="stNumberInput"] button { 
            background-color: #f1f5f9 !important; 
            border-color: #cbd5e1 !important; 
        }
        [data-testid="stNumberInput"] button * { 
            color: #0f172a !important; 
            fill: #0f172a !important; 
        }

        .stButton > button { 
            background-color: #ffffff !important; 
            color: #0f172a !important; 
            border: 1px solid #cbd5e1 !important; 
            border-radius: 8px !important;
            font-weight: 600 !important;
        }
    </style>
    """
    plotly_bg = "#ffffff"
    plotly_paper = "#ffffff"
    plotly_text = "#0f172a"
    plotly_axis = "#0f172a"
    plotly_grid = "#e2e8f0"
    accent_green = "#059669"

st.markdown(theme_css, unsafe_allow_html=True)

# Helper function to apply high-contrast colors and spacing to all Plotly charts
def update_chart_layout(fig):
    fig.update_layout(
        plot_bgcolor=plotly_bg,
        paper_bgcolor=plotly_paper,
        font=dict(color=plotly_text),
        title=dict(
            font=dict(color=plotly_text, size=16),
            y=0.98,
            x=0.01,
            xanchor="left",
            yanchor="top"
        ),
        xaxis=dict(
            tickfont=dict(color=plotly_axis, size=12),
            title=dict(font=dict(color=plotly_axis, size=13)),
            gridcolor=plotly_grid
        ),
        yaxis=dict(
            tickfont=dict(color=plotly_axis, size=12),
            title=dict(font=dict(color=plotly_axis, size=13)),
            gridcolor=plotly_grid
        ),
        legend=dict(font=dict(color=plotly_text)),
        margin=dict(l=15, r=15, t=45, b=15)
    )
    return fig

# --------------------------------------------------
# DATA ENGINE HELPERS
# --------------------------------------------------

BASE_DIR = Path(__file__).parent
SAMPLE_DIR = BASE_DIR / "sample_data"

def prepare_data(raw_df):
    cleaned = clean_energy_data(raw_df)
    if cleaned.empty:
        raise ValueError("The dataset has no valid records.")
        
    daily = aggregate_daily(cleaned)
    if daily.empty:
        raise ValueError("Unable to create daily energy summaries.")
        
    if "consumption_kwh" in daily.columns and "kwh" not in daily.columns:
        daily["kwh"] = daily["consumption_kwh"]
    if "kwh" in daily.columns and "consumption_kwh" not in daily.columns:
        daily["consumption_kwh"] = daily["kwh"]
        
    if "consumption_kwh" in cleaned.columns and "kwh" not in cleaned.columns:
        cleaned["kwh"] = cleaned["consumption_kwh"]
    if "kwh" in cleaned.columns and "consumption_kwh" not in cleaned.columns:
        cleaned["consumption_kwh"] = cleaned["kwh"]
        
    return cleaned, daily

def load_preset_sample(filename):
    file_path = SAMPLE_DIR / filename
    if not file_path.exists():
        dates = pd.date_range(start="2026-10-01", periods=30, freq="D")
        np.random.seed(42)
        vals = np.random.uniform(8.0, 12.0, size=30)
        vals[4] = 24.5
        vals[17] = 28.2
        raw = pd.DataFrame({"timestamp": dates, "consumption_kwh": np.round(vals, 2)})
    else:
        raw = pd.read_csv(file_path)
    return prepare_data(raw)

if "energy_data" not in st.session_state:
    try:
        cleaned, daily = load_preset_sample("normal_usage.csv")
        st.session_state.energy_data = cleaned
        st.session_state.daily_data = daily
        st.session_state.source_name = "normal_usage.csv"
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
# SIDEBAR NAVIGATION
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 🌿 EcoSense")
    st.caption("SMART ENERGY INTELLIGENCE")
    st.divider()

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

    sample_options = {
        "Normal Usage Baseline": "normal_usage.csv",
        "Moderate Spikes Dataset": "spike_usage.csv",
        "High Anomalies Dataset": "high_anamolies.csv",
    }
    selected_sample_label = st.selectbox("📂 Load Preset Sample Dataset", list(sample_options.keys()))
    if st.button("Load Selected Dataset"):
        chosen_file = sample_options[selected_sample_label]
        try:
            cleaned, new_daily = load_preset_sample(chosen_file)
            st.session_state.energy_data = cleaned
            st.session_state.daily_data = new_daily
            st.session_state.source_name = chosen_file
            st.success(f"Loaded {chosen_file}!")
            st.rerun()
        except Exception as e:
            st.error(f"Could not load {chosen_file}: {e}")

    tariff_input = st.number_input(
        "Electricity rate (₹/kWh)",
        min_value=0.0,
        max_value=100.0,
        value=float(st.session_state.get("tariff", 7.0)),
        step=0.5,
    )
    st.session_state.tariff = tariff_input

    st.caption("Current Active Dataset:")
    st.markdown(f'<div class="dataset-badge">📄 {st.session_state.source_name}</div>', unsafe_allow_html=True)

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
        y_val = "consumption_kwh" if "consumption_kwh" in daily.columns else "kwh"
        fig = px.area(
            daily,
            x="timestamp",
            y=y_val,
            markers=True,
            labels={"timestamp": "Date", y_val: "Consumption (kWh)"},
        )
        fig.update_traces(line_color=accent_green, fillcolor="rgba(16, 185, 129, 0.15)")
        fig = update_chart_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Bill & Usage Breakdown")
        st.markdown(
            f"""
            <div class="summary-box">
                <p><b>Lowest Usage:</b> {summary['lowest_usage_kwh']:.2f} kWh</p>
                <p><b>Lowest Usage Date:</b> {summary['lowest_date']}</p>
                <p><b>Recorded Days:</b> {len(daily)}</p>
                <hr style="border-top: 1px solid #cbd5e1; margin: 12px 0;">
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
        if st.button("Restore Default Sample Dataset"):
            cleaned, new_daily = load_preset_sample("normal_usage.csv")
            st.session_state.energy_data = cleaned
            st.session_state.daily_data = new_daily
            st.session_state.source_name = "normal_usage.csv"
            st.success("Default dataset restored.")
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

    y_analytics = "consumption_kwh" if "consumption_kwh" in chart_data.columns else "kwh"

    fig = px.bar(
        chart_data,
        x="timestamp",
        y=y_analytics,
        title=title,
        labels={"timestamp": "Date", y_analytics: "Consumption (kWh)"},
    )
    fig.update_traces(marker_color=accent_green)
    fig = update_chart_layout(fig)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Average Consumption by Weekday")
    y_df = "consumption_kwh" if "consumption_kwh" in df.columns else "kwh"
    weekday_data = df.groupby("day_of_week")[y_df].mean().reindex(range(7)).reset_index()
    weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_data["weekday"] = weekday_data["day_of_week"].map(dict(enumerate(weekday_names)))

    fig_weekday = px.bar(
        weekday_data,
        x="weekday",
        y=y_df,
        labels={"weekday": "Day", y_df: "Avg kWh"},
    )
    fig_weekday.update_traces(marker_color=accent_green)
    fig_weekday = update_chart_layout(fig_weekday)
    st.plotly_chart(fig_weekday, use_container_width=True)

# --------------------------------------------------
# TAB 4: ANOMALY DETECTION
# --------------------------------------------------

elif page == "Anomaly Detection":
    st.header("Anomaly Detection")
    st.caption("Isolation Forest detects readings that deviate significantly from baseline behavior.")

    try:
        anom_df = detect_anomalies(daily)
        anomalies = anom_df[anom_df["is_anomaly"]] if "is_anomaly" in anom_df.columns else pd.DataFrame()

        c1, c2, c3 = st.columns(3)
        with c1: metric_card("Unusual Readings", str(len(anomalies)), "Potential anomalies")
        with c2: metric_card("Normal Readings", str(len(anom_df) - len(anomalies)), "Within expected range")
        with c3: metric_card("Detection Engine", "Isolation Forest", "Unsupervised ML Model")

        st.write("")

        y_anom_col = "kwh" if "kwh" in anom_df.columns else "consumption_kwh"

        fig = px.scatter(
            anom_df,
            x="timestamp",
            y=y_anom_col,
            color="is_anomaly" if "is_anomaly" in anom_df.columns else None,
            color_discrete_map={True: "#ef4444", False: accent_green},
            labels={"timestamp": "Date", y_anom_col: "Consumption (kWh)"},
        )
        fig = update_chart_layout(fig)
        st.plotly_chart(fig, use_container_width=True)

        if not anomalies.empty:
            st.warning(f"Detected {len(anomalies)} unusual spike(s).")
            display_cols = [c for c in ["timestamp", y_anom_col, "z_score", "anomaly_severity"] if c in anomalies.columns]
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
        try:
            forecast_df, eval_metrics = train_and_forecast(daily, forecast_days=horizon_days)
        except TypeError:
            forecast_df, eval_metrics = train_and_forecast(daily, horizon_days)

        c1, c2 = st.columns(2)
        
        mae_val = eval_metrics.get('mae', None)
        mae_str = f"{mae_val:.2f} kWh" if isinstance(mae_val, (int, float)) else "N/A"

        with c1: metric_card("Forecasted Days", f"{horizon_days} Days", "Prediction horizon")
        with c2: metric_card("Validation Error (MAE)", mae_str, "Random Forest accuracy metric")

        st.write("")
        st.write("")
        st.subheader(f"Predicted kWh for Next {horizon_days} Days")

        y_fc_col = "predicted_kwh" if "predicted_kwh" in forecast_df.columns else ("kwh" if "kwh" in forecast_df.columns else forecast_df.columns[1])

        fig_fc = px.bar(
            forecast_df,
            x="timestamp",
            y=y_fc_col,
            labels={"timestamp": "Date", y_fc_col: "Predicted kWh"},
        )
        fig_fc.update_traces(marker_color="#f59e0b")
        fig_fc = update_chart_layout(fig_fc)
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