from pathlib import Path

import pandas as pd
from model import train_data, FEATURES


BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR.parent / "Day1" / "day1_log.txt"

def get_model_result(model, sensor_reading):
    """Predict the machine state using the trained ML model."""
    reading_df = pd.DataFrame([sensor_reading], columns=FEATURES)
    prediction = str(model.predict(reading_df)[0]).strip().upper()

    trouble_states = {
        "TROUBLE",
        "CRITICAL",
        "OVERHEATING",
        "MOTOR_OVERLOAD",
        "HIGH_VIBRATION",
        "LOW_PRESSURE",
    }

    if prediction in trouble_states:
        return "TROUBLE"

    if prediction in {"NORMAL", "NO_TROUBLE"}:
        return "NO_TROUBLE"

    return "INVESTIGATE"


def get_log_result():
    """Read maintenance notes and scan for relevant keywords."""
    if not LOG_FILE.exists():
        print(f"Warning: Maintenance log not found: {LOG_FILE}")
        return "INVESTIGATE"

    with open(LOG_FILE, "r", encoding="utf-8", errors="replace") as file:
        notes = file.read().lower()

    trouble_keywords = [
        "trouble",
        "critical",
        "overheating",
        "motor overload",
        "high vibration",
        "low pressure",
        "fault detected",
    ]

    normal_keywords = [
        "no trouble",
        "normal operation",
        "no fault",
        "operating normally",
    ]

    investigate_keywords = [
        "investigate",
        "inspection required",
        "maintenance required",
        "check machine",
    ]

    if any(keyword in notes for keyword in investigate_keywords):
        return "INVESTIGATE"

    if any(keyword in notes for keyword in normal_keywords):
        return "NO_TROUBLE"

    if any(keyword in notes for keyword in trouble_keywords):
        return "TROUBLE"

    return "NO_TROUBLE"


def combine_logic(model_result, log_result):

    if model_result == "TROUBLE" and log_result == "TROUBLE":
        return "ESCALATE"

    if model_result == "TROUBLE" and log_result == "NO_TROUBLE":
        return "ML PREDICTION TAKES PRIORITY: TROUBLE"

    if log_result == "INVESTIGATE":
        return "INVESTIGATE"

    if model_result == "TROUBLE":
        return "ML PREDICTION TAKES PRIORITY: TROUBLE"

    if model_result == "INVESTIGATE":
        return "INVESTIGATE"

    return "NORMAL"


def main():
    model = train_data()

    sensor_reading = {
        "temperature": 75.0,
        "pressure": 1000.0,
        "vibration": 1.2,
        "rpm": 3500.0,
        "current": 15.0,
    }

    model_result = get_model_result(model, sensor_reading)
    log_result = get_log_result()

    combined_result = combine_logic(model_result, log_result)

    print("\n========== DECISION RESULTS ==========")
    print(f"Model result    : {model_result}")
    print(f"Log result      : {log_result}")
    print(f"Combined result : {combined_result}")
    print("======================================")


if __name__ == "__main__":
    main()
