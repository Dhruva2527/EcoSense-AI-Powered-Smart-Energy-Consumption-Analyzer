"""Member 3: anomaly detection (Isolation Forest).

Input : DataFrame with columns [time_col, value_col]  (default: timestamp, kwh)
Output: same DataFrame + extra columns (see detect_anomalies docstring).
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def detect_anomalies(df, time_col="timestamp", value_col="kwh", contamination=0.02):
    """Flag abnormal consumption.

    Adds columns:
      hour, dow          - calendar features
      typical_kwh        - median usage for that weekday+hour (the 'normal' baseline)
      excess_kwh         - actual minus typical
      anomaly_score      - higher = more abnormal (0..1 scaled)
      is_anomaly         - bool
      severity           - 'Normal' | 'Medium' | 'High' (only for anomalies)
      reason             - short human-readable explanation
    """
    d = df[[time_col, value_col]].copy()
    d[time_col] = pd.to_datetime(d[time_col])
    d = d.sort_values(time_col).reset_index(drop=True)

    d["hour"] = d[time_col].dt.hour
    d["dow"] = d[time_col].dt.dayofweek
    d["typical_kwh"] = d.groupby(["dow", "hour"])[value_col].transform("median")
    d["excess_kwh"] = d[value_col] - d["typical_kwh"]

    # rolling context: how does this reading compare with the last 24 readings?
    roll = d[value_col].rolling(24, min_periods=1).mean().shift(1).bfill()
    d["ratio_to_recent"] = d[value_col] / roll.clip(lower=1e-3)

    feats = d[[value_col, "hour", "dow", "excess_kwh", "ratio_to_recent"]]
    model = IsolationForest(n_estimators=200, contamination=contamination, random_state=42)
    d["is_anomaly"] = model.fit_predict(feats) == -1

    raw = -model.score_samples(feats)  # higher = more abnormal
    d["anomaly_score"] = (raw - raw.min()) / (raw.max() - raw.min() + 1e-9)

    # severity based on how far above/below the baseline the reading is
    spread = d["excess_kwh"].std() + 1e-9
    z = d["excess_kwh"].abs() / spread
    d["severity"] = np.where(~d["is_anomaly"], "Normal", np.where(z > 3, "High", "Medium"))

    def reason(r):
        if not r.is_anomaly:
            return ""
        if r.excess_kwh > 0:
            txt = f"{r.excess_kwh:.2f} kWh above normal for this hour"
            if r.hour <= 5:
                txt += " (night-time usage)"
            return txt
        return f"{abs(r.excess_kwh):.2f} kWh below normal (possible outage or meter fault)"

    d["reason"] = d.apply(reason, axis=1)
    return d.drop(columns=["ratio_to_recent"])


def summarize_anomalies(d, value_col="kwh", time_col="timestamp"):
    """Dict of headline numbers for the dashboard / recommendations module."""
    an = d[d["is_anomaly"]]
    if an.empty:
        return {"count": 0, "pct": 0.0, "extra_kwh": 0.0, "worst_time": None,
                "high_count": 0, "night_count": 0, "table": an}
    worst = an.loc[an["excess_kwh"].abs().idxmax()]
    return {
        "count": int(len(an)),
        "pct": float(len(an) / len(d) * 100),
        "extra_kwh": float(an["excess_kwh"].clip(lower=0).sum()),
        "worst_time": worst[time_col],
        "high_count": int((an["severity"] == "High").sum()),
        "night_count": int((an["hour"] <= 5).sum()),
        "table": an[[time_col, value_col, "typical_kwh", "excess_kwh",
                     "severity", "reason"]].sort_values("excess_kwh", ascending=False),
    }
