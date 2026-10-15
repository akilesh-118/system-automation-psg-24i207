import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from decision_engine import joint_decision
from log_scanner import scan_text
from safety_rules import safety_check
from spoof_detector import detect_spoofing

def test_emergency_is_deterministic():
    readings = {
        "shoulder": {"torque": 50, "temperature": 90, "vibration": 2},
    }
    emergencies, _ = safety_check(readings)
    assert emergencies

def test_missing_sensor_is_not_silently_safe():
    readings = {
        "wrist": {"torque": None, "temperature": 45, "vibration": 1.2},
    }
    emergencies, warnings = safety_check(readings)
    assert not emergencies
    assert warnings

def test_negated_log_does_not_warn():
    score, keywords = scan_text("No unusual noise or vibration observed.")
    assert score == 0
    assert keywords == []

def test_spoof_cross_check():
    readings = {
        "elbow": {"torque": 3, "temperature": 72, "vibration": 6.5}
    }
    previous = {
        "elbow": {"torque": 52, "temperature": 69, "vibration": 5.9}
    }
    findings = detect_spoofing(readings, previous)
    assert findings

def test_priority():
    decision, reason = joint_decision(
        safety_emergency=True,
        spoof=False,
        sensor_integrity_fault=False,
        wear_probability=0.95,
        log_score=5,
    )
    assert decision == "EMERGENCY_STOP"

def test_independent_signals_schedule_maintenance():
    decision, reason = joint_decision(
        safety_emergency=False,
        spoof=False,
        sensor_integrity_fault=False,
        wear_probability=0.90,
        log_score=3,
    )
    assert decision == "SCHEDULE_MAINTENANCE"
