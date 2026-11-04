"""Transparent, agronomy-informed irrigation advisory calculations.

This is a decision-support prototype. It uses a simplified daily water balance
inspired by FAO-56 crop-coefficient methods; it is not a calibrated local model.
"""

from dataclasses import dataclass

LITRES_PER_ACRE_MM = 4046.86

CROPS = {
    "Rice": {"kc": 1.15, "root_depth_cm": 35, "depletion": 0.20, "emoji": "🌾"},
    "Wheat": {"kc": 1.05, "root_depth_cm": 75, "depletion": 0.45, "emoji": "🌿"},
    "Tomato": {"kc": 1.10, "root_depth_cm": 50, "depletion": 0.35, "emoji": "🍅"},
    "Cotton": {"kc": 1.10, "root_depth_cm": 90, "depletion": 0.50, "emoji": "🌱"},
    "Groundnut": {"kc": 0.95, "root_depth_cm": 45, "depletion": 0.45, "emoji": "🥜"},
}

STAGES = {"Initial growth": 0.55, "Development": 0.80, "Mid-season": 1.00, "Late season": 0.75}
SOILS = {
    "Sandy": {"available_water_mm_per_m": 90, "infiltration": 0.90},
    "Loamy": {"available_water_mm_per_m": 150, "infiltration": 0.80},
    "Clayey": {"available_water_mm_per_m": 170, "infiltration": 0.65},
}


@dataclass
class Advisory:
    action: str
    urgency: str
    net_mm: float
    gross_mm: float
    litres_per_acre: int
    daily_need_mm: float
    effective_rain_mm: float
    depletion_mm: float
    threshold_mm: float
    reasons: list[str]
    weekly: list[dict]


def advise(crop: str, stage: str, soil: str, moisture_pct: float,
           eto_mm_day: float, rain_forecast_mm: float) -> Advisory:
    """Estimate a 7-day irrigation plan from crop, soil, and weather inputs."""
    profile, soil_profile = CROPS[crop], SOILS[soil]
    stage_kc = profile["kc"] * STAGES[stage]
    daily_need = max(0.0, eto_mm_day) * stage_kc
    root_zone_capacity = soil_profile["available_water_mm_per_m"] * profile["root_depth_cm"] / 100
    depletion = root_zone_capacity * (1 - min(max(moisture_pct, 0), 100) / 100)
    threshold = root_zone_capacity * profile["depletion"]
    effective_rain = max(0.0, rain_forecast_mm) * soil_profile["infiltration"]

    reasons = [f"{crop} at {stage.lower()} uses about {daily_need:.1f} mm of water per day.",
               f"The estimated root zone holds {root_zone_capacity:.0f} mm; current depletion is {depletion:.0f} mm."]
    if effective_rain >= daily_need * 2:
        net_mm, action, urgency = 0.0, "Wait for rain", "Rain likely"
        reasons.append(f"Forecast rain may supply {effective_rain:.1f} mm after soil infiltration losses.")
    elif depletion <= threshold and effective_rain >= daily_need:
        net_mm, action, urgency = 0.0, "Recheck tomorrow", "Moisture adequate"
        reasons.append("Root-zone moisture is above the crop's estimated irrigation trigger.")
        reasons.append("Expected effective rain can cover roughly the next day's water use.")
    else:
        target_refill = max(0.0, depletion - threshold * 0.35)
        net_mm = max(0.0, min(target_refill, daily_need * 3.5) - effective_rain)
        if net_mm < 2:
            net_mm, action, urgency = 0.0, "Recheck tomorrow", "Low need"
        else:
            action, urgency = "Irrigate today", "Priority" if depletion > threshold * 1.5 else "Soon"
            reasons.append(f"Effective forecast rain offsets {min(effective_rain, target_refill):.1f} mm of the refill need.")
            reasons.append("The suggested amount is capped to about 3.5 days of crop demand to limit overwatering.")

    gross_mm = net_mm / soil_profile["infiltration"] if net_mm else 0.0
    litres = round(gross_mm * LITRES_PER_ACRE_MM)
    weekly = []
    balance = depletion
    for day in range(7):
        rain = effective_rain if day == 1 else 0.0
        balance = max(0.0, balance + daily_need - rain - (gross_mm * soil_profile["infiltration"] if day == 0 else 0.0))
        weekly.append({"Day": ["Today", "Tomorrow", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"][day],
                       "Crop water use (mm)": round(daily_need, 1),
                       "Effective rain (mm)": round(rain, 1),
                       "Root-zone depletion (mm)": round(balance, 1)})
    return Advisory(action, urgency, round(net_mm, 1), round(gross_mm, 1), litres,
                    round(daily_need, 1), round(effective_rain, 1), round(depletion, 1),
                    round(threshold, 1), reasons, weekly)
