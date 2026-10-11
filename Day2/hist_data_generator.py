
import csv
import random

# File configuration
CSV_FILE = "sensor_history.csv"
TOTAL_ROWS = 300

random.seed(42)


# Generate simulated sensor data
def generate_sensor_data():
    return {
        "temperature": round(random.uniform(20, 95), 1),
        "pressure": round(random.uniform(950, 1050), 1),
        "vibration": round(random.uniform(0, 2), 1),
        "rpm": round(random.uniform(1100, 6000), 1),
        "current": round(random.uniform(5, 20), 1),
    }


# Classify the machine state using sensor thresholds
def classify_state(reading):
    temperature = reading["temperature"]
    pressure = reading["pressure"]
    vibration = reading["vibration"]
    rpm = reading["rpm"]
    current = reading["current"]

    # Critical conditions take priority
    if (
        temperature >= 85
        or temperature <= 25
        or pressure >= 1040
        or pressure <= 960
        or vibration >= 1.8
        or vibration <= 0.2
        or rpm >= 5800
        or rpm <= 1200
        or current >= 18
    ):
        return "Trouble"

    # Warning conditions
    if (
        temperature >= 70
        or temperature <= 40
        or pressure >= 1025
        or pressure <= 980
        or vibration >= 1.2
        or vibration <= 0.4
        or rpm >= 5000
        or rpm <= 1500
        or current >= 15
        or current <= 8
    ):
        return "Warning"

    return "Normal"


# Create the sensor history CSV file
def generate_csv():
    fieldnames = [
        "temperature",
        "pressure",
        "vibration",
        "rpm",
        "current",
        "state",
    ]

    state_counts = {
        "Normal": 0,
        "Warning": 0,
        "Trouble": 0,
    }

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for _ in range(TOTAL_ROWS):
            reading = generate_sensor_data()
            state = classify_state(reading)
            reading["state"] = state

            writer.writerow(reading)
            state_counts[state] += 1

    print(f"\nCSV file created successfully: {CSV_FILE}")
    print(f"Total records: {TOTAL_ROWS}")
    print("\nState distribution:")

    for state, count in state_counts.items():
        print(f"{state}: {count} ({count / TOTAL_ROWS * 100:.1f}%)")


if __name__ == "__main__":
    generate_csv()
