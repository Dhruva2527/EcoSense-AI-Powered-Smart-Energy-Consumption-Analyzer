import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

from modules.data_cleaner import (
    clean_energy_data,
    aggregate_daily,
    compute_summary_analytics,
)
from modules.anomaly_detection import detect_anomalies
from modules.prediction import train_and_forecast, forecast_summary
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

# Keep the selected theme between Streamlit reruns.
if "theme" not in st.session_state:
    st.session_state.theme = "Light"

# --------------------------------------------------
# WHITE AND GREEN THEME
# --------------------------------------------------

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

# Dark mode overrides. The default Light theme keeps the white-and-green design.
if st.session_state.theme == "Dark":
    st.markdown("""
    <style>
        :root { color-scheme: dark; }
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
            background: #0F172A !important;
            color: #F8FAFC !important;
        }
        [data-testid="stHeader"] { background: #0F172A !important; }
        [data-testid="stSidebar"] {
            background: #1E293B !important;
            border-right: 1px solid #334155 !important;
        }
        .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3,
        .stApp h4, .stApp li, .stApp [data-testid="stMarkdownContainer"],
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span {
            color: #F8FAFC !important;
        }
        .stApp [data-testid="stCaptionContainer"] { color: #CBD5E1 !important; }
        .main-title, .metric-value, .section-title { color: #34D399 !important; }
        .subtitle, .metric-label, .metric-note, .footer { color: #CBD5E1 !important; }
        .metric-card, .section-card, .summary-box {
            background: #1E293B !important;
            border-color: #334155 !important;
        }
        [data-testid="stFileUploader"] section,
        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stTextArea"] textarea,
        [data-baseweb="select"] > div,
        [data-baseweb="popover"], [role="listbox"], [role="option"] {
            background: #334155 !important;
            color: #F8FAFC !important;
            border-color: #64748B !important;
            -webkit-text-fill-color: #F8FAFC !important;
        }
        [data-testid="stFileUploader"] section *,
        [data-testid="stTextInput"] input::placeholder,
        [data-testid="stTextArea"] textarea::placeholder,
        [data-baseweb="select"] *, [role="option"] * {
            color: #F8FAFC !important;
        }
        [data-testid="stDataFrame"], [data-testid="stTable"] {
            background: #1E293B !important;
        }
        [data-testid="stAlert"] p { color: #F8FAFC !important; }
        .recommendation { background: #183A2A !important; }
    </style>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

BASE_DIR = Path(__file__).parent
SAMPLE_FILE = BASE_DIR / "sample_data" / "normal_usage.csv"


def prepare_data(raw_df):
    """Clean input data and prepare the model-compatible columns."""
    cleaned = clean_energy_data(raw_df)

    if cleaned.empty:
        raise ValueError("The dataset has no valid records.")

    # The ML modules expect the column name 'kwh'.
    cleaned["kwh"] = cleaned["consumption_kwh"]

    daily = aggregate_daily(cleaned)

    if daily.empty:
        raise ValueError("Unable to create daily energy summaries.")

    # The anomaly and recommendation modules use 'kwh'.
    daily_model = daily.copy()
    daily_model["kwh"] = daily_model["consumption_kwh"]

    return cleaned, daily, daily_model


def load_sample_data():
    if not SAMPLE_FILE.exists():
        raise FileNotFoundError(
            "sample_data/normal_usage.csv was not found."
        )

    raw = pd.read_csv(SAMPLE_FILE)
    return prepare_data(raw)


if "energy_data" not in st.session_state:
    try:
        cleaned, daily, daily_model = load_sample_data()
        st.session_state.energy_data = cleaned
        st.session_state.daily_data = daily
        st.session_state.daily_model = daily_model
        st.session_state.source_name = "Normal usage sample dataset"
    except Exception as error:
        st.error(f"Could not load sample data: {error}")
        st.stop()


df = st.session_state.energy_data.copy()
daily = st.session_state.daily_data.copy()
daily_model = st.session_state.daily_model.copy()

tariff = st.session_state.get("tariff", 7.0)


# --------------------------------------------------
# COMMON METRICS
# --------------------------------------------------

summary = compute_summary_analytics(daily)

if not summary:
    st.error("No summary information is available.")
    st.stop()

bill = estimate_electricity_cost(
    summary["total_kwh"],
    rate_per_kwh=tariff,
)


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
# HEADER AND NAVIGATION
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🌿 EcoSense</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Smart Energy Consumption Analyzer'
    '</div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🌿 EcoSense")
    st.caption("SMART ENERGY INTELLIGENCE")
    st.divider()

    theme_choice = st.radio(
        "App Theme",
        ["Light", "Dark"],
        index=0 if st.session_state.theme == "Light" else 1,
        horizontal=True,
    )
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

    tariff = st.number_input(
        "Electricity rate (₹/kWh)",
        min_value=0.0,
        max_value=100.0,
        value=float(st.session_state.get("tariff", 7.0)),
        step=0.5,
    )

    st.session_state.tariff = tariff

    st.caption("Current dataset")
    st.write(st.session_state.source_name)


# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

if page == "Overview":

    st.header("Energy Overview")
    st.caption("A snapshot of your electricity consumption.")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Total Consumption",
            f'{summary["total_kwh"]:,.2f} kWh',
            "Total recorded usage",
        )

    with c2:
        metric_card(
            "Daily Average",
            f'{summary["daily_avg_kwh"]:,.2f} kWh',
            "Average daily consumption",
        )

    with c3:
        metric_card(
            "Peak Consumption",
            f'{summary["peak_usage_kwh"]:,.2f} kWh',
            summary["peak_date"],
        )

    with c4:
        metric_card(
            "Estimated Electricity Bill",
            f'₹{bill["total_estimated_cost"]:,.2f}',
            f"Rate: ₹{tariff:.2f}/kWh",
        )

    st.divider()

    left, right = st.columns([1.6, 1])

    with left:
        st.subheader("Daily Energy Consumption")

        fig = px.area(
            daily,
            x="timestamp",
            y="consumption_kwh",
            markers=True,
            labels={
                "timestamp": "Date",
                "consumption_kwh": "Consumption (kWh)",
            },
        )

        fig.update_traces(
            line_color="#198747",
            fillcolor="rgba(25,135,71,0.12)",
        )

        fig.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
        )

        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Usage Summary")

        st.write("**Lowest usage**")
        st.write(f'{summary["lowest_usage_kwh"]:.2f} kWh')

        st.write("**Lowest usage date**")
        st.write(summary["lowest_date"])

        st.write("**Recorded days**")
        st.write(len(daily))

        st.write("**Estimated energy charge**")
        st.write(f'₹{bill["energy_charge"]:,.2f}')

        st.write("**Fixed charge**")
        st.write(f'₹{bill["fixed_charge"]:,.2f}')

        st.write("**Estimated tax**")
        st.write(f'₹{bill["tax_charge"]:,.2f}')

        st.info(
            "The electricity bill is an estimate based on the "
            "configured rate and simplified fixed-charge and tax assumptions."
        )


# --------------------------------------------------
# UPLOAD DATA
# --------------------------------------------------

elif page == "Upload Data":

    st.header("Upload Energy Dataset")

    st.write(
        "Upload a CSV file containing timestamp and consumption_kwh columns."
    )

    uploaded_file = st.file_uploader(
        "Choose your CSV file",
        type=["csv"],
    )

    st.caption("Expected columns: timestamp, consumption_kwh")

    if uploaded_file is not None:

        try:
            raw = pd.read_csv(uploaded_file)

            cleaned, new_daily, new_daily_model = prepare_data(raw)

            st.success(
                f"Successfully cleaned {len(cleaned):,} records."
            )

            st.write("Dataset preview")
            st.dataframe(
                cleaned.head(10),
                use_container_width=True,
                hide_index=True,
            )

            st.write(
                f"Date range: {cleaned['timestamp'].min()} "
                f"to {cleaned['timestamp'].max()}"
            )

            if st.button("Use Uploaded Dataset", type="primary"):

                st.session_state.energy_data = cleaned
                st.session_state.daily_data = new_daily
                st.session_state.daily_model = new_daily_model
                st.session_state.source_name = uploaded_file.name

                st.success("Dataset successfully activated!")
                st.rerun()

        except Exception as error:
            st.error(f"Unable to process CSV: {error}")

    st.divider()

    st.subheader("Active Dataset")

    st.dataframe(
        df.head(10),
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download Active Dataset",
        df.to_csv(index=False).encode("utf-8"),
        "ecosense_cleaned_data.csv",
        "text/csv",
    )

    if st.button("Restore Sample Dataset"):

        try:
            cleaned, new_daily, new_daily_model = load_sample_data()

            st.session_state.energy_data = cleaned
            st.session_state.daily_data = new_daily
            st.session_state.daily_model = new_daily_model
            st.session_state.source_name = "Normal usage sample dataset"

            st.success("Sample dataset restored.")
            st.rerun()

        except Exception as error:
            st.error(f"Unable to restore sample data: {error}")


# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------

elif page == "Analytics":

    st.header("Energy Analytics")

    period = st.selectbox(
        "Select analysis period",
        ["Daily", "Weekly", "Monthly"],
    )

    if period == "Daily":

        chart_data = daily.copy()
        title = "Daily Consumption"

    elif period == "Weekly":

        chart_data = (
            df.set_index("timestamp")
            .resample("W")["consumption_kwh"]
            .sum()
            .reset_index()
        )
        title = "Weekly Consumption"

    else:

        chart_data = (
            df.set_index("timestamp")
            .resample("MS")["consumption_kwh"]
            .sum()
            .reset_index()
        )
        title = "Monthly Consumption"

    fig = px.bar(
        chart_data,
        x="timestamp",
        y="consumption_kwh",
        title=title,
        labels={
            "timestamp": "Date",
            "consumption_kwh": "Consumption (kWh)",
        },
    )

    fig.update_traces(marker_color="#269653")

    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Consumption by Weekday")

    weekday_data = (
        df.groupby("day_of_week")["consumption_kwh"]
        .mean()
        .reindex(range(7))
        .reset_index()
    )

    weekday_names = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday",
    ]

    weekday_data["weekday"] = weekday_data["day_of_week"].map(
        dict(enumerate(weekday_names))
    )

    weekday_fig = px.bar(
        weekday_data,
        x="weekday",
        y="consumption_kwh",
        labels={
            "weekday": "Day",
            "consumption_kwh": "Average consumption (kWh)",
        },
    )

    weekday_fig.update_traces(marker_color="#198747")

    st.plotly_chart(weekday_fig, use_container_width=True)

    st.subheader("Daily Statistics")

    st.dataframe(
        daily[
            ["timestamp", "consumption_kwh"]
        ].rename(
            columns={
                "timestamp": "Date",
                "consumption_kwh": "Consumption (kWh)",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


# --------------------------------------------------
# ANOMALY DETECTION
# --------------------------------------------------

elif page == "Anomaly Detection":

    st.header("Anomaly Detection")

    st.caption(
        "Isolation Forest identifies readings that differ from "
        "the usual consumption pattern."
    )

    try:

        anomaly_data = detect_anomalies(
            df,
            time_col="timestamp",
            value_col="kwh",
        )

        anomalies = anomaly_data[
            anomaly_data["is_anomaly"]
        ]

        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card(
                "Unusual Readings",
                str(len(anomalies)),
                "Potential anomalies",
            )

        with c2:
            metric_card(
                "Normal Readings",
                str(len(anomaly_data) - len(anomalies)),
                "Within expected pattern",
            )

        with c3:
            metric_card(
                "Detection Method",
                "Isolation Forest",
                "Unsupervised machine learning",
            )

        fig = px.scatter(
            anomaly_data,
            x="timestamp",
            y="kwh",
            color="is_anomaly",
            color_discrete_map={
                True: "#dc4545",
                False: "#198747",
            },
            labels={
                "timestamp": "Date and Time",
                "kwh": "Consumption (kWh)",
                "is_anomaly": "Anomaly",
            },
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Detected Unusual Readings")

        if anomalies.empty:
            st.success("No unusual readings were detected.")
        else:
            st.warning(
                f"{len(anomalies)} unusual reading(s) detected. "
                "An anomaly does not automatically mean energy wastage."
            )

            st.dataframe(
                anomalies[
                    [
                        "timestamp",
                        "kwh",
                        "typical_kwh",
                        "excess_kwh",
                        "severity",
                        "reason",
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

    except Exception as error:
        st.error(f"Anomaly detection failed: {error}")


# --------------------------------------------------
# PREDICTIONS
# --------------------------------------------------

elif page == "Predictions":

    st.header("Energy Consumption Forecast")

    horizon_days = st.slider(
        "Forecast duration (days)",
        min_value=3,
        max_value=14,
        value=7,
    )

    if st.button("Generate Forecast", type="primary"):

        try:

            with st.spinner("Training Random Forest model..."):

                forecast_df, model_metrics = train_and_forecast(
                    df,
                    horizon_hours=horizon_days * 24,
                    time_col="timestamp",
                    value_col="kwh",
                )

            st.session_state.forecast_df = forecast_df
            st.session_state.forecast_metrics = model_metrics

            st.success("Forecast generated successfully!")

        except Exception as error:
            st.error(f"Unable to generate forecast: {error}")

    if "forecast_df" in st.session_state:

        forecast_df = st.session_state.forecast_df
        model_metrics = st.session_state.forecast_metrics

        forecast_totals = forecast_summary(
            forecast_df,
            tariff,
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card(
                "Forecast Consumption",
                f'{forecast_totals["total_kwh"]:.2f} kWh',
                "For selected forecast period",
            )

        with c2:
            metric_card(
                "Estimated Energy Cost",
                f'₹{forecast_totals["est_cost"]:,.2f}',
                "Forecast energy charge only",
            )

        with c3:
            metric_card(
                "Model MAE",
                f'{model_metrics["mae"]:.3f}',
                "Validation error in kWh",
            )

        history_chart = daily[["timestamp", "consumption_kwh"]].copy()
        history_chart = history_chart.rename(
            columns={"consumption_kwh": "kwh"}
        )
        history_chart["Type"] = "Historical"

        future_chart = forecast_df[
            ["timestamp", "kwh"]
        ].copy()
        future_chart["Type"] = "Forecast"

        combined = pd.concat(
            [history_chart, future_chart],
            ignore_index=True,
        )

        fig = px.line(
            combined,
            x="timestamp",
            y="kwh",
            color="Type",
            markers=True,
            color_discrete_map={
                "Historical": "#198747",
                "Forecast": "#e49b28",
            },
            labels={
                "timestamp": "Date",
                "kwh": "Consumption (kWh)",
            },
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Forecast Results")

        st.dataframe(
            forecast_df,
            use_container_width=True,
            hide_index=True,
        )

        st.download_button(
            "Download Forecast CSV",
            forecast_df.to_csv(index=False).encode("utf-8"),
            "ecosense_forecast.csv",
            "text/csv",
        )

        st.write("**Model:**", model_metrics["model_name"])
        st.write("**Frequency detected:**", model_metrics["freq"])
        st.write("**Training rows:**", model_metrics["train_rows"])
        st.write("**RMSE:**", round(model_metrics["rmse"], 3))
        st.write("**MAPE:**", f'{model_metrics["mape"]:.2f}%')

        st.caption(
            "Forecasts are estimates based on historical data. "
            "Accuracy depends on the quantity and quality of readings."
        )


# --------------------------------------------------
# RECOMMENDATIONS
# --------------------------------------------------

elif page == "Recommendations":

    st.header("Smart Energy Recommendations")

    try:

        recommendation_anomalies = detect_anomalies(
            daily_model,
            time_col="timestamp",
            value_col="kwh",
        )

        score, recommendations = calculate_energy_score_and_recs(
            daily,
            recommendation_anomalies,
        )

        st.subheader("Energy Efficiency Score")

        c1, c2 = st.columns([1, 2])

        with c1:
            st.metric(
                "Efficiency Score",
                f"{score}/100",
            )

            st.progress(score / 100)

        with c2:

            if score >= 80:
                st.success("Good energy efficiency performance.")
            elif score >= 50:
                st.warning("There is room to improve energy efficiency.")
            else:
                st.error("Your consumption pattern needs attention.")

        st.divider()

        st.subheader("Recommended Actions")

        for recommendation in recommendations:

            with st.container(border=True):

                st.markdown(
                    f"### {recommendation['title']}"
                )

                st.write(recommendation["body"])

                if recommendation["type"] == "warning":
                    st.warning("Attention required")
                elif recommendation["type"] == "success":
                    st.success("Positive trend")
                else:
                    st.info("General recommendation")

    except Exception as error:
        st.error(f"Unable to generate recommendations: {error}")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div class="footer">
        🌿 EcoSense | Understand Your Energy. Detect Waste. Save Smarter.
    </div>
    """,
    unsafe_allow_html=True,
)