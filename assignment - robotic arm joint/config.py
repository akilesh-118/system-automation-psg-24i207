# System thresholds and configuration for the robotic arm monitor.

TORQUE_EMERGENCY_NM = 85.0
TEMPERATURE_EMERGENCY_C = 85.0
VIBRATION_EMERGENCY_MMS = 8.0

TORQUE_WARNING_PCT = 70.0
TEMPERATURE_WARNING_C = 65.0
VIBRATION_WARNING_MMS = 4.0

# A missing/invalid safety-critical reading is unsafe to ignore.
SENSOR_INTEGRITY_MAINTENANCE = True

# Spoofing: a suspiciously low torque while heat and vibration are high.
SPOOF_TORQUE_LOW_NM = 12.5
SPOOF_TEMPERATURE_C = 68.0
SPOOF_VIBRATION_MMS = 5.5
MAX_BELIEVABLE_TORQUE_STEP_NM = 25.0

HIGH_WEAR_PROBABILITY = 0.75
MEDIUM_WEAR_PROBABILITY = 0.40
