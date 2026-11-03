#member 2

import pandas as pd
import numpy as np

def clean_energy_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validates, cleans, and engineers features for energy consumption datasets.
    Handles raw timestamp parsing, missing values, and negative readings.
    """
    df_clean = df.copy()
    
    # Standardize column headers to lowercase & trimmed
    df_clean.columns = df_clean.columns.str.strip().str.lower()
    
    if 'timestamp' not in df_clean.columns or 'consumption_kwh' not in df_clean.columns:
        raise ValueError("CSV must contain 'timestamp' and 'consumption_kwh' columns.")
        
    # Convert and validate timestamps
    df_clean['timestamp'] = pd.to_datetime(df_clean['timestamp'], errors='coerce')
    df_clean = df_clean.dropna(subset=['timestamp']).sort_values('timestamp').reset_index(drop=True)
    
    # Clean numeric consumption data
    df_clean['consumption_kwh'] = pd.to_numeric(df_clean['consumption_kwh'], errors='coerce')
    
    # Forward-fill then back-fill missing consumption values
    df_clean['consumption_kwh'] = df_clean['consumption_kwh'].ffill().bfill()
    
    # Replace negative or zero readings with zero or minimum realistic positive reading
    df_clean['consumption_kwh'] = df_clean['consumption_kwh'].apply(lambda x: max(0.0, float(x)))
    
    # Extract temporal features
    df_clean['hour'] = df_clean['timestamp'].dt.hour
    df_clean['day_of_week'] = df_clean['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
    df_clean['day'] = df_clean['timestamp'].dt.day
    df_clean['month'] = df_clean['timestamp'].dt.month
    df_clean['is_weekend'] = df_clean['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
    
    return df_clean

def aggregate_daily(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregates raw data logs into daily totals and averages."""
    daily_df = df.resample('D', on='timestamp').agg({
        'consumption_kwh': 'sum',
        'is_weekend': 'max'
    }).reset_index()
    
    daily_df['day_of_week'] = daily_df['timestamp'].dt.dayofweek
    daily_df['month'] = daily_df['timestamp'].dt.month
    return daily_df

def compute_summary_analytics(daily_df: pd.DataFrame) -> dict:
    """Computes high-level summary statistics for the Overview UI dashboard."""
    if daily_df.empty:
        return {}
        
    total_usage = float(daily_df['consumption_kwh'].sum())
    daily_avg = float(daily_df['consumption_kwh'].mean())
    max_day_row = daily_df.loc[daily_df['consumption_kwh'].idxmax()]
    min_day_row = daily_df.loc[daily_df['consumption_kwh'].idxmin()]
    
    return {
        "total_kwh": round(total_usage, 2),
        "daily_avg_kwh": round(daily_avg, 2),
        "peak_usage_kwh": round(float(max_day_row['consumption_kwh']), 2),
        "peak_date": max_day_row['timestamp'].strftime('%Y-%m-%d'),
        "lowest_usage_kwh": round(float(min_day_row['consumption_kwh']), 2),
        "lowest_date": min_day_row['timestamp'].strftime('%Y-%m-%d')
    }

if __name__ == "__main__":
    # Local Member 2 Test Script
    raw_dummy = pd.DataFrame({
        'timestamp': ['2026-10-01 00:00', '2026-10-01 01:00', '2026-10-02 00:00', 'invalid_date'],
        'consumption_kwh': ['0.5', '-0.2', '12.4', '1.0']
    })
    
    cleaned = clean_energy_data(raw_dummy)
    daily = aggregate_daily(cleaned)
    stats = compute_summary_analytics(daily)
    
    print("Cleaned Data:")
    print(cleaned)
    print("\nSummary Analytics:")
    print(stats)