
"""
DAY 1 · HANDS-ON — Build Your Rule Engine
23IF02 System Automation

Work through the TODOs in order. Each one matches a step on the
"Hands-on · Build Your Rule Engine" slide. Run this file after each
step to see your progress:

    python hands_on_starter.py

Need the answer? See hands_on_solution.py — but try it yourself first.
"""

import random
import time

LOG_FILE = "day1_log.txt"


# ---------------------------------------------------------------------------
# STEP 1 — Generate simulated sensor data
# ---------------------------------------------------------------------------
def generate_sensor_data():
    """Return a dict with at least 'temperature', 'pressure', 'vibration'."""
    # TODO: fill in realistic random values, e.g. temperature 50-95 (deg C)
    reading = {
        "temperature": random.randint(50, 95),
        "pressure": round(random.uniform(20, 50), 2),
        "vibration": round(random.uniform(0, 1), 2),
        "current": round(random.uniform(5, 120), 2),
    }

    # STRETCH GOAL (after the 8 steps below all work): real sensors aren't
    # perfectly clean. Try making one field randomly return None (a
    # dropout) or spike far outside its normal range every so often, then
    # update evaluate_rules() so a dropout doesn't crash your engine.
    if random.random() < 0.05:
        sensor = random.choice(list(reading.keys()))
        reading[sensor] = None

    return reading


# ---------------------------------------------------------------------------
# STEP 2 — Write your first automation rules
# STEP 7 — Add a rule of your own (add another dict to this list)
# STEP 8 — Add one priority rule (lower "priority" number checked first)
# ---------------------------------------------------------------------------

RULES = [
    # Critical conditions
    {
        "name": "CRITICAL_TEMP",
        "priority": 1,
        "condition": lambda r: r["temperature"] > 90,
        "action": "STOP_MACHINE"
    },
    {
        "name": "HIGH_TEMP",
        "priority": 2,
        "condition": lambda r: r["temperature"] > 80,
        "action": "STOP_MACHINE"
    },
    {
        "name": "LOW_PRESSURE",
        "priority": 3,
        "condition": lambda r: r["pressure"] < 30,
        "action": "STOP_MACHINE"
    },
    {
        "name": "HIGH_PRESSURE",
        "priority": 4,
        "condition": lambda r: r["pressure"] > 45,
        "action": "STOP_MACHINE"
    },
    {
        "name": "HIGH_VIBRATION",
        "priority": 5,
        "condition": lambda r: r["vibration"] > 0.8,
        "action": "STOP_MACHINE"
    },
    {
        "name": "CURRENT_SPIKE",
        "priority": 6,
        "condition": lambda r: r["current"] > 100,
        "action": "STOP_MACHINE"
    },

    # Warning conditions
    {
        "name": "TEMP_WARNING",
        "priority": 7,
        "condition": lambda r: r["temperature"] > 70,
        "action": "RAISE_WARNING"
    },
    {
        "name": "PRESSURE_WARNING",
        "priority": 8,
        "condition": lambda r: r["pressure"] > 40,
        "action": "RAISE_WARNING"
    },
    {
        "name": "VIBRATION_WARNING",
        "priority": 9,
        "condition": lambda r: r["vibration"] > 0.5,
        "action": "RAISE_WARNING"
    },
    {
        "name": "CURRENT_WARNING",
        "priority": 10,
        "condition": lambda r: r["current"] > 80,
        "action": "RAISE_WARNING"
    },

    # Alert conditions
    {
        "name": "LOW_TEMP_ALERT",
        "priority": 11,
        "condition": lambda r: r["temperature"] < 55,
        "action": "RAISE_ALERT"
    },
    {
        "name": "LOW_VIBRATION_ALERT",
        "priority": 12,
        "condition": lambda r: r["vibration"] < 0.1,
        "action": "RAISE_ALERT"
    }
]


# ---------------------------------------------------------------------------
# STEP 3 — Detect machine state from the rules
# ---------------------------------------------------------------------------
def evaluate_rules(reading, rules):
    """Return (rule_name, action) for the first matching rule, checked in
    priority order (lowest number first). If nothing matches, return
    ("NO_RULE_FIRED", "CONTINUE_NORMAL")."""

    # Check if any sensor data is missing
    required_sensors = ["temperature", "pressure", "vibration", "current"]

    missing = [
        sensor for sensor in required_sensors
        if sensor not in reading or reading[sensor] is None
    ]

    # If any value is missing, flag the sensor dropout
    if missing:
        return (
            "SENSOR_DROPOUT: " + ", ".join(missing),
            "FLAG_MISSING_DATA"
        )

    # TODO: sort `rules` by priority, then check each rule's condition(reading)
    # Lower priority number means the rule is checked first
    sorted_rules = sorted(rules, key=lambda rule: rule["priority"])

    # Check each rule in priority order
    for rule in sorted_rules:
        if rule["condition"](reading):
            return rule["name"], rule["action"]

    # If no rule matches, continue normal operation
    return "NO_RULE_FIRED", "CONTINUE_NORMAL"


# ---------------------------------------------------------------------------
# STEP 4 — Trigger an action when a rule fires
# ---------------------------------------------------------------------------
def take_action(action):
    """Return a human-readable string describing what happens for this action."""

    if action == "STOP_MACHINE":
        return "Machine stop requested due to a critical condition."
    elif action == "RAISE_ALERT":
        return "ALERT: Immediate attention required!"
    elif action == "RAISE_WARNING":
        return "WARNING: Check the machine condition."
    elif action == "CONTINUE_NORMAL":
        return "Machine operating normally."
    elif action == "FLAG_MISSING_DATA":
        return "SENSOR DROPOUT: Missing sensor data detected."
    else:
        return f"(no handler yet for action: {action})"


# ---------------------------------------------------------------------------
# STEP 5 — Log every decision made
# ---------------------------------------------------------------------------
def log_decision(reading, rule_name, action):
    """Append one line to LOG_FILE with the reading, rule fired, and action."""

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(
            f"Time: {timestamp} | "
            f"Reading: {reading} | "
            f"Rule: {rule_name} | "
            f"Action: {action}\n"
        )


# ---------------------------------------------------------------------------
# STEP 6 — Add a second sensor to the system
# TODO: add e.g. "current" to generate_sensor_data(), then use it in a rule
# ---------------------------------------------------------------------------


def main():
    for tick in range(1, 11):
        reading = generate_sensor_data()
        rule_name, action = evaluate_rules(reading, RULES)
        outcome = take_action(action)

        print(f"[Tick {tick:02d}] SENSE -> {reading}")
        print(f"           THINK -> {rule_name}")
        print(f"           ACT   -> {outcome}\n")

        log_decision(reading, rule_name, action)
        time.sleep(0.2)


if __name__ == "__main__":
    main()
