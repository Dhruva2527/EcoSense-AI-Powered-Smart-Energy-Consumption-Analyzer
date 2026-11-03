def estimate_electricity_cost(total_kwh: float, rate_per_kwh: float = 7.0) -> dict:
    """
    Calculates estimated total cost based on energy consumed (kWh)
    and electricity tariff rates.
    """
    base_cost = float(total_kwh) * float(rate_per_kwh)
    fixed_charge = 100.0  # Base fixed connection charge
    tax_estimate = base_cost * 0.09  # 9% tax/duty estimate
    total_bill = base_cost + fixed_charge + tax_estimate
    
    return {
        "energy_charge": round(base_cost, 2),
        "fixed_charge": round(fixed_charge, 2),
        "tax_charge": round(tax_estimate, 2),
        "total_estimated_cost": round(total_bill, 2)
    }

if __name__ == "__main__":
    # Test script locally
    res = estimate_electricity_cost(150.0, rate_per_kwh=7.0)
    print("Cost Estimate Test Output:", res)