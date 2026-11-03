"""Quick self-test for Member 3. Run: python test_ml.py"""
import numpy as np, pandas as pd
from modules.anomaly_detection import detect_anomalies, summarize_anomalies
from modules.prediction import train_and_forecast, forecast_summary

rng = np.random.default_rng(0)
idx = pd.date_range("2025-06-01", periods=24 * 60, freq="h")
h = idx.hour.values
kwh = 0.4 + 0.5*np.exp(-((h-8)**2)/6) + 1.1*np.exp(-((h-20)**2)/8) + rng.normal(0, .08, len(idx))
spikes = rng.choice(len(idx), 8, replace=False); kwh[spikes] += 3.5
df = pd.DataFrame({"timestamp": idx, "kwh": np.clip(kwh, .05, None)})

d = detect_anomalies(df, contamination=0.02)
s = summarize_anomalies(d)
caught = d.loc[spikes, "is_anomaly"].mean()
print(f"anomalies={s['count']}  injected spikes caught={caught:.0%}  high-severity={s['high_count']}")

fc, m = train_and_forecast(df, horizon_hours=168)
print(f"MAE={m['mae']:.3f}  RMSE={m['rmse']:.3f}  MAPE={m['mape']:.1f}%  rows={m['train_rows']}")
print(forecast_summary(fc, 7.0))

daily = df.set_index("timestamp").resample("D").sum().reset_index()
fc2, m2 = train_and_forecast(daily, horizon_hours=168)
print("daily mode:", m2["freq"], len(fc2), "steps, MAE", round(m2["mae"], 2))
