"""
EcoSense Core Intelligence Modules
----------------------------------
Includes data cleaning, statistical analytics, Isolation Forest anomaly detection,
Random Forest time-series forecasting, cost estimation, and recommendation engines.
"""

from .data_cleaner import clean_energy_data, aggregate_daily, compute_summary_analytics
from .anomaly_detection import detect_anomalies
from .prediction import train_and_forecast
from .cost_estimator import estimate_electricity_cost
from .recommendations import calculate_energy_score_and_recs

__all__ = [
    "clean_energy_data",
    "aggregate_daily",
    "compute_summary_analytics",
    "detect_anomalies",
    "train_and_forecast",
    "estimate_electricity_cost",
    "calculate_energy_score_and_recs",
]
