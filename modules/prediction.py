
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

FEATS = ["hour", "dow", "month", "lag_1", "lag_day", "lag_week", "roll_day"]


def _prep_series(df, time_col, value_col):
    s = df.set_index(pd.to_datetime(df[time_col]))[value_col].sort_index()
    step = s.index.to_series().diff().median()
    freq = "D" if step >= pd.Timedelta(hours=20) else "h"
    s = s.resample(freq).mean().interpolate(limit=12).dropna()
    return s, freq


def _lags(freq):
    # (steps in one day, steps in one week)
    return (1, 7) if freq == "D" else (24, 168)


def _build(s, freq):
    day, week = _lags(freq)
    f = pd.DataFrame({"y": s})
    f["hour"] = f.index.hour if freq == "h" else 0
    f["dow"] = f.index.dayofweek
    f["month"] = f.index.month
    f["lag_1"] = f["y"].shift(1)
    f["lag_day"] = f["y"].shift(day)
    f["lag_week"] = f["y"].shift(week)
    f["roll_day"] = f["y"].shift(1).rolling(day).mean()
    return f.dropna()


def _row(ts, hist, freq):
    day, week = _lags(freq)
    delta = pd.Timedelta(hours=1) if freq == "h" else pd.Timedelta(days=1)
    return [
        ts.hour if freq == "h" else 0, ts.dayofweek, ts.month,
        hist[ts - delta], hist[ts - day * delta], hist[ts - week * delta],
        np.mean([hist[ts - k * delta] for k in range(1, day + 1)]),
    ]


def train_and_forecast(df, horizon_hours=168, time_col="timestamp", value_col="kwh"):
    """Return (forecast_df, metrics).

    forecast_df: columns [timestamp, kwh, lower, upper]  (lower/upper = ~80% band)
    metrics    : dict(mae, rmse, mape, model_name, train_rows, freq)
    """
    s, freq = _prep_series(df, time_col, value_col)
    day, week = _lags(freq)
    if len(s) < week * 3:
        raise ValueError(f"Need at least {week * 3} {'days' if freq == 'D' else 'hours'} of data to forecast.")

    f = _build(s, freq)
    hold = week  # hold out last week for validation
    tr, te = f.iloc[:-hold], f.iloc[-hold:]

    model = RandomForestRegressor(n_estimators=200, min_samples_leaf=2, n_jobs=-1, random_state=42)
    model.fit(tr[FEATS], tr["y"])
    pred = model.predict(te[FEATS])
    resid = te["y"].values - pred
    metrics = {
        "mae": float(mean_absolute_error(te["y"], pred)),
        "rmse": float(np.sqrt(mean_squared_error(te["y"], pred))),
        "mape": float(np.mean(np.abs(resid) / np.clip(te["y"].values, 0.05, None)) * 100),
        "model_name": "RandomForestRegressor (recursive)",
        "train_rows": int(len(f)),
        "freq": freq,
    }

    # refit on everything and roll forward
    model.fit(f[FEATS], f["y"])
    steps = horizon_hours if freq == "h" else max(1, horizon_hours // 24)
    delta = pd.Timedelta(hours=1) if freq == "h" else pd.Timedelta(days=1)
    future = pd.date_range(s.index[-1] + delta, periods=steps, freq=freq)
    hist = s.to_dict()
    preds = []
    for ts in future:
        x = pd.DataFrame([_row(ts, hist, freq)], columns=FEATS)
        p = float(model.predict(x)[0])
        hist[ts] = p
        preds.append(p)

    band = 1.28 * resid.std()
    out = pd.DataFrame({"timestamp": future, "kwh": preds})
    out["lower"] = (out["kwh"] - band).clip(lower=0)
    out["upper"] = out["kwh"] + band
    return out, metrics


def forecast_summary(fc, price_per_kwh):
    """Headline numbers for the dashboard."""
    return {
        "total_kwh": float(fc["kwh"].sum()),
        "est_cost": float(fc["kwh"].sum() * price_per_kwh),
        "peak_time": fc.loc[fc["kwh"].idxmax(), "timestamp"],
        "peak_kwh": float(fc["kwh"].max()),
    }
