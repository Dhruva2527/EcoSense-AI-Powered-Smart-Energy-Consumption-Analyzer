import pandas as pd
from typing import Tuple, List, Dict

def calculate_energy_score_and_recs(daily_df: pd.DataFrame, anom_df: pd.DataFrame) -> Tuple[int, List[Dict[str, str]]]:
    """
    Evaluates system metrics to compute an Energy Efficiency Score (0-100)
    and output actionable rule-based recommendations.
    """
    score = 100
    recommendations = []
    
    # Anomaly frequency penalty
    anomaly_count = anom_df['is_anomaly'].sum() if ('is_anomaly' in anom_df.columns and not anom_df.empty) else 0
    
    if anomaly_count > 0:
        score -= min(30, anomaly_count * 10)
        recommendations.append({
            "type": "warning",
            "title": "Unusual Consumption Spikes Detected",
            "body": f"Detected {anomaly_count} day(s) with abnormal energy usage. Inspect high-wattage equipment (AC, water heaters, EV chargers) during those dates."
        })

    # Usage trend evaluation
    if len(daily_df) >= 7:
        recent_avg = daily_df['consumption_kwh'].tail(3).mean()
        overall_avg = daily_df['consumption_kwh'].mean()
        
        if overall_avg > 0 and recent_avg > overall_avg * 1.2:
            score -= 15
            recommendations.append({
                "type": "warning",
                "title": "Recent Upward Consumption Trend",
                "body": f"Your average daily usage over the past 3 days ({recent_avg:.1f} kWh) is more than 20% higher than your overall average ({overall_avg:.1f} kWh)."
            })
        elif overall_avg > 0 and recent_avg < overall_avg * 0.9:
            recommendations.append({
                "type": "success",
                "title": "Efficiency Improvement",
                "body": "Great job! Your recent energy usage is noticeably lower than your overall baseline."
            })
            
    if not recommendations:
        recommendations.append({
            "type": "info",
            "title": "Stable Consumption Pattern",
            "body": "Your energy consumption remains within expected baseline levels. Keep maintaining efficient usage habits."
        })
        
    final_score = max(0, min(100, score))
    return final_score, recommendations

if __name__ == "__main__":
    # Test script locally
    dummy_daily = pd.DataFrame({'consumption_kwh': [8.5, 9.0, 9.2, 8.8, 10.0, 9.5, 9.1]})
    dummy_anom = pd.DataFrame({'is_anomaly': [False, False, False, False, False, False, False]})
    s, r = calculate_energy_score_and_recs(dummy_daily, dummy_anom)
    print("Test Score:", s)
    print("Test Recs:", r)