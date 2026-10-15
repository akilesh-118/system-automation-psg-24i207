from config import (
    SPOOF_TORQUE_LOW_NM,
    SPOOF_TEMPERATURE_C,
    SPOOF_VIBRATION_MMS,
    MAX_BELIEVABLE_TORQUE_STEP_NM,
)

def detect_spoofing(readings, previous=None):
    findings = []

    for joint, r in readings.items():
        torque = r.get("torque")
        temp = r.get("temperature")
        vibration = r.get("vibration")

        if torque is None:
            continue

        if (
            torque < SPOOF_TORQUE_LOW_NM
            and temp is not None and temp >= SPOOF_TEMPERATURE_C
            and vibration is not None and vibration >= SPOOF_VIBRATION_MMS
        ):
            findings.append(
                (joint,
                 f"torque {torque} Nm is implausibly low (< {SPOOF_TORQUE_LOW_NM}) "
                 f"while temperature {temp} C and vibration {vibration} mm/s are elevated")
            )

        if previous and joint in previous:
            old = previous[joint].get("torque")
            if old is not None and abs(torque - old) > MAX_BELIEVABLE_TORQUE_STEP_NM:
                findings.append(
                    (joint,
                     f"torque changed by {abs(torque-old):.1f} Nm in one sample "
                     f"(max believable {MAX_BELIEVABLE_TORQUE_STEP_NM} Nm)")
                )

    return findings
