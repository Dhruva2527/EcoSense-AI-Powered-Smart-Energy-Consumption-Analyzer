"""Electricity cost estimation helpers for EcoSense.

The default ₹6.50/kWh rate is a demo assumption for the hackathon.
It is not an official Karnataka tariff or a complete utility bill calculation.
"""

import pandas as pd

TARIFF_PER_KWH = 6.50


def _validate_usage_data(df):
    required = {"timestamp", "consumption_kwh"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    if df.empty:
        raise ValueError("The electricity dataset is empty.")

    usage = pd.to_numeric(df["consumption_kwh"], errors="coerce")
    if usage.isna().any():
        raise ValueError("consumption_kwh contains missing or non-numeric values.")
    if (usage < 0).any():
        raise ValueError("consumption_kwh cannot contain negative values.")

    return usage


def calculate_total_cost(df, tariff_per_kwh=TARIFF_PER_KWH):
    """Return estimated total cost for all readings in the DataFrame."""
    usage = _validate_usage_data(df)
    return round(float(usage.sum() * tariff_per_kwh), 2)


def calculate_daily_cost(df, tariff_per_kwh=TARIFF_PER_KWH):
    """Return a Series indexed by date, containing estimated daily costs."""
    usage = _validate_usage_data(df)
    timestamps = pd.to_datetime(df["timestamp"], errors="coerce")
    if timestamps.isna().any():
        raise ValueError("timestamp contains invalid date/time values.")

    daily_units = usage.groupby(timestamps.dt.date).sum()
    return (daily_units * tariff_per_kwh).round(2)


def calculate_average_daily_cost(df, tariff_per_kwh=TARIFF_PER_KWH):
    daily_cost = calculate_daily_cost(df, tariff_per_kwh)
    return round(float(daily_cost.mean()), 2)


def get_cost_summary(df, tariff_per_kwh=TARIFF_PER_KWH):
    usage = _validate_usage_data(df)
    total_units = float(usage.sum())

    return {
        "total_units_kwh": round(total_units, 2),
        "tariff_per_kwh": round(float(tariff_per_kwh), 2),
        "total_cost_rupees": calculate_total_cost(df, tariff_per_kwh),
        "average_daily_cost_rupees": calculate_average_daily_cost(
            df, tariff_per_kwh
        ),
    }
