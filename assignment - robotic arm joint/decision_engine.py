from config import HIGH_WEAR_PROBABILITY, MEDIUM_WEAR_PROBABILITY

def joint_decision(safety_emergency, spoof, sensor_integrity_fault,
                   wear_probability, log_score):
    # Priority is intentionally safety-first:
    # P1 hard safety threshold
    # P2 spoof/security inconsistency
    # P3 missing/invalid safety-critical reading
    # P4 independent ML + maintenance evidence agree
    # P5 single warning signal
    # P6 no warning
    if safety_emergency:
        return "EMERGENCY_STOP", "P1 safety threshold"
    if spoof:
        return "EMERGENCY_STOP", "P2 spoof cross-check"
    if sensor_integrity_fault:
        return "SCHEDULE_MAINTENANCE", "P3 sensor-integrity floor"

    high_wear = wear_probability is not None and wear_probability >= HIGH_WEAR_PROBABILITY
    medium_wear = wear_probability is not None and wear_probability >= MEDIUM_WEAR_PROBABILITY

    if high_wear and log_score > 0:
        return "SCHEDULE_MAINTENANCE", "P4 two independent signals agree"
    if high_wear:
        return "MONITOR", "P5 single signal"
    if medium_wear or log_score > 0:
        return "MONITOR", "P5 single signal"

    return "SAFE", "P6 no warning signals"

def arm_decision(joint_results):
    priority = {
        "EMERGENCY_STOP": 4,
        "SCHEDULE_MAINTENANCE": 3,
        "MONITOR": 2,
        "SAFE": 1,
    }
    return max(
        (result["decision"] for result in joint_results.values()),
        key=lambda d: priority[d]
    )
