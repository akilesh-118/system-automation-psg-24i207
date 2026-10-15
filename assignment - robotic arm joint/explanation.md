# Short Technical Explanation

## 1. Safety thresholds

The system uses deterministic emergency thresholds for torque, temperature, and vibration. A reading at or above any emergency threshold immediately produces `EMERGENCY_STOP`. The values are deliberately chosen as clearly dangerous operating limits for this synthetic project: torque 85 N*m, temperature 85 C, and vibration 8 mm/s RMS. These are project assumptions, not manufacturer limits.

This check is intentionally independent of machine learning. A predictive model can be wrong or unavailable, but the hard safety rule must still operate.

## 2. Predictive wear and maintenance-log combination

A synthetic historical dataset of 120 labelled readings is used to train a shallow decision-tree classifier. The model uses torque percentage of the emergency limit, temperature, and vibration to estimate the probability that a joint is worn.

Technician notes are processed separately using an explainable keyword/rule scanner. Relevant words include terms such as grinding, rattling, vibration, hot, stiff, and unusual. Simple negation is handled so a sentence such as "No unusual noise or vibration observed" does not become a false warning.

The two signals are combined by the decision engine. If the ML model predicts high wear and the maintenance log independently reports a relevant warning for the same joint, the result is `SCHEDULE_MAINTENANCE`. If only one signal is present, the safer intermediate action is normally `MONITOR`.

## 3. Spoofed-sensor defense

The spoof detector performs cross-sensor consistency checks. A very low torque value is suspicious when the same joint is simultaneously hot and experiencing high vibration. A large one-sample torque change compared with the previous reading is also flagged.

This defense can catch a torque-only spoof that attempts to mask a real mechanical problem while temperature and vibration remain trustworthy. It would not reliably catch an attacker who simultaneously spoofs all independent sensor channels in a mutually consistent way. Therefore, the implementation does not claim to solve every possible cyberattack.

## 4. Final decision priority

The system uses explicit priority because industrial safety decisions must override lower-priority predictions:

1. Hard safety threshold -> `EMERGENCY_STOP`
2. Sensor spoof/integrity anomaly -> `EMERGENCY_STOP`
3. Missing/invalid safety-critical sensor -> `SCHEDULE_MAINTENANCE`
4. High ML wear + maintenance evidence -> `SCHEDULE_MAINTENANCE`
5. One warning signal -> `MONITOR`
6. No warning signals -> `SAFE`

This gives one final decision per arm while keeping the safety-critical path deterministic and explainable.

## 5. Demonstration

The included demo fleet reaches all four required outcomes. `ARM-04` demonstrates that an emergency stop works without needing the ML model. `ARM-05` demonstrates the difference between processing the spoofed reading normally and detecting the spoofing attempt.
