from config import (
    TORQUE_EMERGENCY_NM,
    TEMPERATURE_EMERGENCY_C,
    VIBRATION_EMERGENCY_MMS,
    TORQUE_WARNING_PCT,
    TEMPERATURE_WARNING_C,
    VIBRATION_WARNING_MMS,
)

def _invalid(value):
    return value is None or not isinstance(value, (int, float))

def safety_check(readings):
    """Deterministic safety check. It never calls the ML model.

    Only clearly dangerous physical thresholds produce an emergency here.
    Missing/invalid readings are returned as warnings and are escalated by
    the decision engine to SCHEDULE_MAINTENANCE.
    """
    emergencies = []
    warnings = []

    for joint, r in readings.items():
        if any(_invalid(r.get(k)) for k in ("torque", "temperature", "vibration")):
            warnings.append((joint, ["missing/invalid sensor reading"]))
            continue

        reasons = []
        if r["torque"] >= TORQUE_EMERGENCY_NM:
            reasons.append(f"torque {r['torque']} Nm >= emergency limit {TORQUE_EMERGENCY_NM} Nm")
        if r["temperature"] >= TEMPERATURE_EMERGENCY_C:
            reasons.append(f"temperature {r['temperature']} C >= emergency limit {TEMPERATURE_EMERGENCY_C} C")
        if r["vibration"] >= VIBRATION_EMERGENCY_MMS:
            reasons.append(f"vibration {r['vibration']} mm/s >= emergency limit {VIBRATION_EMERGENCY_MMS} mm/s")

        if reasons:
            emergencies.extend((joint, x) for x in reasons)
            continue

        warning_reasons = []
        if r["torque"] >= TORQUE_WARNING_PCT / 100 * TORQUE_EMERGENCY_NM:
            warning_reasons.append("high torque")
        if r["temperature"] >= TEMPERATURE_WARNING_C:
            warning_reasons.append("high temperature")
        if r["vibration"] >= VIBRATION_WARNING_MMS:
            warning_reasons.append("high vibration")

        if warning_reasons:
            warnings.append((joint, warning_reasons))

    return emergencies, warnings
