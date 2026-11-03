# 🌿 EcoSense – AI-Powered Smart Energy Consumption Analyzer

> **Understand Your Energy. Detect Waste. Save Smarter.**

EcoSense is a Python-based AI and data analytics application designed to help households and energy managers understand electricity usage patterns, detect hidden waste using unsupervised machine learning, forecast upcoming energy demand, and receive data-driven energy efficiency suggestions.

---

## ⚡ The Problem

Traditional utility bills present total consumption (kWh) and final charges, but fail to provide actionable context:
* **Why** did electricity usage suddenly increase?
* **Which** specific dates experienced abnormal consumption spikes?
* **How much** electricity is expected to be consumed next month?
* **What** concrete actions can be taken to prevent waste?

EcoSense bridges this gap by converting raw time-series smart meter data into real-time operational intelligence.

---

## 🚀 Key Features

* **📊 Energy Overview & Analytics:** Computes total usage, daily averages, peak consumption dates, and tariff-based cost estimates with interactive trend visualizations.
* **🚨 AI-Driven Anomaly Detection:** Implements an **Isolation Forest** model coupled with rolling **Z-score statistics** to isolate and categorize abnormal energy usage spikes without requiring labeled historical waste data.
* **🔮 Predictive Energy Demand:** Uses a **Random Forest Regressor** trained on engineered temporal lags ($t-1$, $t-7$, 7-day rolling average) to project multi-step energy demand (3–14 days ahead) with mean error metrics.
* **💡 Energy Intelligence Scoring:** Evaluates pattern variances to assign an **Energy Efficiency Score (0–100)** alongside context-aware energy-saving recommendations.
* **📁 Dataset Flexibility:** Supports instant sample data generation, raw CSV upload, and exportable forecast CSV reports.

---

## 🛠️ Architecture & Tech Stack

```text
EcoSense Framework
├── Interface: Streamlit Dashboard & Plotly Express Visuals
├── Preprocessing: Pandas, NumPy (Data Cleaning & Aggregations)
├── Machine Learning: Scikit-learn (Isolation Forest & Random Forest Regressor)
└── Financial Engine: Tariff Calculation & Surcharge Estimator
