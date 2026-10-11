
import random
import pandas as pd
from model import train_data, FEATURES

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
        return "TROUBLE", f"ML predicted {prediction}"

    return "NO_TROUBLE", f"ML predicted {prediction}"


def get_rule_result(reading):
    thresholds = {
        "temperature": (25, 40, 70, 85),
        "pressure": (960, 980, 1025, 1040),
        "vibration": (0.2, 0.4, 1.2, 1.8),
        "rpm": (1200, 1500, 5000, 5800),
        "current": (None, 8, 15, 18),
    }

    sensor_details = []
    trouble_found = False
    warning_found = False

    for sensor, value in reading.items():
        trouble_low, warning_low, warning_high, trouble_high = thresholds[sensor]

        if trouble_low is not None and value <= trouble_low:
            sensor_details.append(f"{sensor} = {value} -> LOW (TROUBLE)")
            trouble_found = True

        elif value >= trouble_high:
            sensor_details.append(f"{sensor} = {value} -> HIGH (TROUBLE)")
            trouble_found = True

        elif warning_low is not None and value <= warning_low:
            sensor_details.append(f"{sensor} = {value} -> LOW (WARNING)")
            warning_found = True

        elif value >= warning_high:
            sensor_details.append(f"{sensor} = {value} -> HIGH (WARNING)")
            warning_found = True

    if trouble_found:
        return "TROUBLE", sensor_details

    if warning_found:
        return "WARNING", sensor_details

    return "NORMAL", ["All sensors are within normal limits"]


def combine_logic(model_result, rule_result):
    if model_result == "TROUBLE" and rule_result == "TROUBLE":
        return "ESCALATE"

    if model_result == "TROUBLE" and rule_result == "WARNING":
        return "TROUBLE"

    if model_result == "TROUBLE" and rule_result == "NORMAL":
        return "WARNING"

    if model_result == "NO_TROUBLE" and rule_result == "TROUBLE":
        return "WARNING"

    if model_result == "NO_TROUBLE" and rule_result == "WARNING":
        return "WARNING"

    return "NORMAL"


def main():
    print("Training model...")
    model = train_data()

    print("\nModel training completed.")
    print(f"Running {NUMBER_OF_TESTS} tests...")

    for test_number in range(1, NUMBER_OF_TESTS + 1):
        reading = generate_random_reading()

        model_result, model_reason = get_model_result(model, reading)
        rule_result, sensor_details = get_rule_result(reading)
        combined_result = combine_logic(model_result, rule_result)

        print("\n" + "=" * 55)
        print(f"TEST CASE {test_number}")
        print("-" * 55)

        print("Sensor readings:")
        for name, value in reading.items():
            print(f"  {name:12}: {value}")

        print(f"\nML result       : {model_result}")
        print(f"ML reason       : {model_reason}")
        print(f"\nRule result     : {rule_result}")
        print("Sensor details  :")

        for detail in sensor_details:
            print(f"  {detail}")

        print(f"\nCombined result : {combined_result}")

    print("\nAll tests completed.")


if __name__ == "__main__":
    main()
