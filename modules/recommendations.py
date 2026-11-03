"""Rule-based energy-saving recommendations for EcoSense."""

RECOMMENDATION_RULES = {
    "HIGH_SPIKE": {
        "title": "Unusual Consumption Spike Detected",
        "action": (
            "Electricity usage is unusually high. Check heavy appliances "
            "such as an air conditioner, geyser, washing machine or refrigerator. "
            "Compare the reading with your usual usage before taking action."
        ),
        "priority": "High",
    },
    "WEEKEND_HIGH": {
        "title": "Elevated Weekend Usage Pattern",
        "action": (
            "Weekend electricity consumption is higher than weekdays. "
            "Switch off unused appliances and avoid leaving devices on standby."
        ),
        "priority": "Medium",
    },
    "UPWARD_TREND": {
        "title": "Continuous Usage Increase",
        "action": (
            "Electricity consumption has increased over several days. "
            "Review daily usage and check appliances that may be running unnecessarily."
        ),
        "priority": "Medium",
    },
    "HIGH_BILL": {
        "title": "High Estimated Electricity Cost",
        "action": (
            "Your estimated electricity cost is high for the selected period. "
            "Review high-consumption hours and reduce avoidable usage."
        ),
        "priority": "Medium",
    },
    "NORMAL": {
        "title": "Normal Electricity Usage",
        "action": (
            "Your electricity consumption looks within the expected demo pattern. "
            "Continue following energy-saving habits."
        ),
        "priority": "Low",
    },
}


def get_recommendations(alert_types):
    """Convert alert codes from the detection module into recommendation details.

    Example:
        get_recommendations(["HIGH_SPIKE", "HIGH_BILL"])
    """
    if alert_types is None:
        alert_types = []

    if isinstance(alert_types, str):
        alert_types = [alert_types]

    recommendations = []
    seen = set()

    for alert in alert_types:
        alert = str(alert).strip().upper()
        if alert in RECOMMENDATION_RULES and alert not in seen:
            recommendations.append({
                "code": alert,
                **RECOMMENDATION_RULES[alert],
            })
            seen.add(alert)

    if not recommendations:
        recommendations.append({
            "code": "NORMAL",
            **RECOMMENDATION_RULES["NORMAL"],
        })

    return recommendations
