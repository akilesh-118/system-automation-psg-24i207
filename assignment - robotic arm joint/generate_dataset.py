import csv
import random
from pathlib import Path

OUT = Path(__file__).parent / "data" / "historical_readings.csv"

def clip(x, low, high):
    return max(low, min(high, x))

def generate(n=120, seed=42):
    rng = random.Random(seed)
    rows = []

    for i in range(n):
        worn = rng.random() < 0.42

        if worn:
            torque = clip(rng.gauss(61, 5), 45, 80)
            temperature = clip(rng.gauss(66, 6), 48, 82)
            vibration = clip(rng.gauss(5.2, 1.1), 2.8, 8.5)
        else:
            torque = clip(rng.gauss(53, 6), 25, 70)
            temperature = clip(rng.gauss(55, 7), 30, 75)
            vibration = clip(rng.gauss(2.8, 0.8), 0.8, 5.0)

        # Add overlap so the classification task is not perfectly trivial.
        if i % 17 == 0:
            torque = clip(rng.gauss(59, 4), 45, 70)
            temperature = clip(rng.gauss(63, 5), 45, 75)
            vibration = clip(rng.gauss(3.4, 0.7), 1.5, 5.5)

        rows.append({
            "arm_id": f"ARM-{(i % 10) + 1:02d}",
            "joint": ["shoulder", "elbow", "wrist"][i % 3],
            "torque_nm": round(torque, 2),
            "temperature_c": round(temperature, 2),
            "vibration_mms": round(vibration, 2),
            "wear_label": int(worn),
        })

    # Small amount of label noise makes the synthetic dataset less artificial.
    for row in rng.sample(rows, 6):
        row["wear_label"] = 1 - row["wear_label"]

    rng.shuffle(rows)

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    worn_count = sum(r["wear_label"] for r in rows)
    print(f"Wrote {OUT}: {len(rows)} rows ({worn_count} worn, {len(rows)-worn_count} healthy)")

if __name__ == "__main__":
    generate()
