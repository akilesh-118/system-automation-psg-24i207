import random
from pathlib import Path

import pandas as pd
from model import train_data, FEATURES

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR.parent / "Day1" / "day1_log.txt"

NUMBER_OF_TESTS = 10
random.seed(42)


def generate_random_reading():
    return {
        "temperature": round(random.uniform(20, 95), 1),
        "pressure": round(random.uniform(950, 1050), 1),
        "vibration": round(random.uniform(0, 2), 2),
        "rpm": round(random.uniform(1100, 6000), 0),
        "current": round(random.uniform(5, 20), 1),
    }

def get_model_result(model, reading):
    reading_df = pd.DataFrame([reading], columns=FEATURES)

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
    if not LOG_FILE.exists():
        print(f"WARNING: Maintenance log not found: {LOG_FILE}")
        return "INVESTIGATE"

    with open(
        LOG_FILE, "r", encoding="utf-8", errors="replace"
    ) as file:
        notes = file.read().lower()

    investigate_keywords = [
        "investigate",
        "inspection required",
        "maintenance required",
        "check machine",
    ]

    trouble_keywords = [
        "overheating",
        "motor overload",
        "high vibration",
        "low pressure",
        "fault detected",
        "critical",
        "trouble detected",
    ]

    normal_keywords = [
        "no trouble",
        "no fault",
        "normal operation",
        "operating normally",
    ]

    if any(word in notes for word in investigate_keywords):
        return "INVESTIGATE"

    if any(word in notes for word in normal_keywords):
        return "NO_TROUBLE"

    if any(word in notes for word in trouble_keywords):
        return "TROUBLE"

    return "NO_TROUBLE"


def combine_logic(model_result, log_result):

    if model_result == "TROUBLE" and log_result == "TROUBLE":
        return "ESCALATE"

    if model_result == "TROUBLE":
        return "ML PREDICTION TAKES PRIORITY: TROUBLE"

    if log_result == "INVESTIGATE":
        return "INVESTIGATE"

    # Investigate if the model itself is uncertain.
    if model_result == "INVESTIGATE":
        return "INVESTIGATE"

    return "NORMAL"


def main():
    print("Training model using the faculty dataset...")
    model = train_data()

    print("\nModel training completed.")

    log_result = get_log_result()

    print(f"Maintenance log: {LOG_FILE}")
    print(f"Log result: {log_result}")
    print(f"\nRunning {NUMBER_OF_TESTS} random tests...")

    for test_number in range(1, NUMBER_OF_TESTS + 1):
        reading = generate_random_reading()

        model_result = get_model_result(model, reading)

        combined_result = combine_logic(
            model_result, log_result
        )

        print("\n" + "=" * 50)
        print(f"TEST CASE {test_number}")
        print("-" * 50)

        print("Sensor reading:")
        for sensor, value in reading.items():
            print(f"  {sensor:12}: {value}")

        print(f"\nModel result    : {model_result}")
        print(f"Log result      : {log_result}")
        print(f"Combined result : {combined_result}")

    print("\n" + "=" * 50)
    print("All random tests completed.")


if __name__ == "__main__":
    main()