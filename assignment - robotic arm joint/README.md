# Robotic Arm Joint Health Monitoring System

**Course:** 23IF02 — System Automation  
**Assignment:** Bonus Challenge — Robotic Arm Joint Health Monitoring System

## Objective

This project monitors the health of robotic-arm joints using a hybrid automation pipeline:

1. Deterministic safety rules
2. Predictive wear model
3. Free-text maintenance-log scanning
4. Sensor-spoofing detection
5. Priority-based final decision engine

The final decision for each arm is one of:

- `SAFE`
- `MONITOR`
- `SCHEDULE_MAINTENANCE`
- `EMERGENCY_STOP`

## Why a hybrid system?

Safety-critical decisions must not depend on an ML model. Therefore, hard emergency thresholds are checked first and independently.

```text
Sensor readings
      |
      +--> Deterministic safety rules ----> EMERGENCY_STOP
      |
      +--> Spoof/integrity validation ---> EMERGENCY_STOP
      |
      +--> Wear prediction
      |
      +--> Maintenance log scanner
                   |
                   v
             Decision engine
                   |
         +---------+---------+
         |         |         |
       SAFE      MONITOR   SCHEDULE_MAINTENANCE
```

## Project structure

```text
robotic_arm_joint_health_monitor/
├── main.py
├── generate_dataset.py
├── config.py
├── safety_rules.py
├── wear_model.py
├── log_scanner.py
├── spoof_detector.py
├── decision_engine.py
├── requirements.txt
├── README.md
├── explanation.md
├── data/
│   ├── historical_readings.csv
│   ├── maintenance_log.txt
│   └── sample_fleet.json
└── tests/
    └── test_system.py
```

## Installation

```bash
pip install -r requirements.txt
```

## Run

The historical dataset is already included. To regenerate it:

```bash
python generate_dataset.py
```

Then run:

```bash
python main.py
```

## Test

```bash
python -m pytest -q
```

## Synthetic dataset

`data/historical_readings.csv` contains 120 labelled historical readings with:

- arm ID
- joint
- torque
- temperature
- vibration
- wear label

The dataset is intentionally synthetic and includes overlapping cases and small label noise so that the model is not simply given a perfectly separable toy dataset.

## Maintenance log

`data/maintenance_log.txt` contains more than eight technician notes. Some notes are relevant to joint health and some are irrelevant.

The scanner handles simple negation. For example:

```text
No unusual noise or vibration observed.
```

is not counted as a warning.

## Spoofing defense

The system checks for a torque reading that is implausibly low while temperature and vibration are elevated. It also checks for an implausibly large one-sample torque jump when a previous reading is available.

This can catch the assignment's example of a fake low torque value used to hide a physically abnormal joint.

It cannot guarantee detection if an attacker simultaneously compromises all independent signals.

## Four required outcomes

The demo fleet contains cases for all four required decisions:

| Arm | Expected result | Main reason |
|---|---|---|
| ARM-01 | SAFE | Normal sensors + no relevant log warning |
| ARM-02 | MONITOR | Maintenance note indicates wrist vibration |
| ARM-03 | SCHEDULE_MAINTENANCE | ML wear prediction + maintenance evidence |
| ARM-04 | EMERGENCY_STOP | Temperature crosses hard safety limit |

ARM-05 additionally demonstrates the spoofing defense.

## Decision priority

```text
P1  Safety threshold              -> EMERGENCY_STOP
P2  Spoof/integrity inconsistency -> EMERGENCY_STOP
P3  Missing critical sensor       -> SCHEDULE_MAINTENANCE
P4  ML + maintenance agree        -> SCHEDULE_MAINTENANCE
P5  Single warning signal         -> MONITOR
P6  No warning signals            -> SAFE
```

## Important safety property

The immediate safety check is implemented in `safety_rules.py` and does not call the ML model. The system can therefore perform the emergency decision even if the model is unavailable.
