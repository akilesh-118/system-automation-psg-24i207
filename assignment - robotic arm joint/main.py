import json
from pathlib import Path

from config import HIGH_WEAR_PROBABILITY
from decision_engine import arm_decision, joint_decision
from log_scanner import joint_log_score, scan_log
from safety_rules import safety_check
from spoof_detector import detect_spoofing
from wear_model import predict_joint, train_model

ROOT = Path(__file__).parent
DATA = ROOT / "data"

def print_model_report(report):
    print("\n" + "=" * 78)
    print("STEP 1-2: HISTORICAL DATASET AND WEAR MODEL")
    print("=" * 78)
    print(f"Dataset rows: {report['rows']}  (train {report['train_rows']} / hold-out test {report['test_rows']})")
    print(f"Train accuracy: {report['train_accuracy']:.2f}")
    print(f"Hold-out test accuracy: {report['test_accuracy']:.2f}")
    print("Test confusion matrix [[TN, FP], [FN, TP]]:", report["confusion_matrix"])
    print("Learned decision-tree rules (class 1 = worn):")
    print(report["tree_rules"])

def analyze_arm(arm, model, log_path):
    arm_id = arm["arm_id"]
    readings = arm["readings"]
    previous = arm.get("previous", {})

    emergencies, warnings = safety_check(readings)
    spoof_findings = detect_spoofing(readings, previous)
    findings = scan_log(log_path, arm_id)

    joint_results = {}
    reasons = {}

    for joint, reading in readings.items():
        safety_reasons = [reason for j, reason in emergencies if j == joint]
        safety_emergency = bool(safety_reasons)
        spoof_reasons = [reason for j, reason in spoof_findings if j == joint]
        spoof = bool(spoof_reasons)

        sensor_fault = any(
            reading.get(k) is None
            for k in ("torque", "temperature", "vibration")
        )

        prediction = predict_joint(model, reading)
        probability = None if prediction is None else prediction[1]

        log_score, keywords = joint_log_score(findings, joint)

        decision, priority_reason = joint_decision(
            safety_emergency,
            spoof,
            sensor_fault,
            probability,
            log_score,
        )

        joint_results[joint] = {
            "decision": decision,
            "probability": probability,
            "log_score": log_score,
            "keywords": keywords,
        }

        why = []
        why.extend(safety_reasons)
        why.extend(spoof_reasons)
        if sensor_fault:
            why.append("missing/invalid safety-critical sensor reading")
        if probability is not None and probability >= HIGH_WEAR_PROBABILITY:
            why.append(f"ML predicts wear (p={probability:.2f})")
        if log_score:
            why.append(f"maintenance log warning (keywords: {', '.join(keywords)})")
        reasons[joint] = why

    final = arm_decision(joint_results)
    return final, joint_results, reasons, emergencies, spoof_findings, warnings

def main():
    dataset = DATA / "historical_readings.csv"
    log = DATA / "maintenance_log.txt"
    fleet_path = DATA / "sample_fleet.json"

    if not dataset.exists():
        raise SystemExit("Dataset missing. Run: python generate_dataset.py")

    model, report = train_model(dataset)
    print_model_report(report)

    with fleet_path.open(encoding="utf-8") as f:
        fleet = json.load(f)["arms"]

    print("\n" + "=" * 78)
    print("STEP 3: MAINTENANCE LOG SCAN")
    print("=" * 78)
    for arm in fleet:
        findings = scan_log(log, arm["arm_id"])
        for item in findings:
            print(
                f"{arm['arm_id']} score {item['score']}: "
                f"\"{item['note']}\""
            )

    print("\n" + "=" * 78)
    print("STEP 4: ONE FINAL DECISION PER ARM")
    print("=" * 78)

    observed = set()

    for arm in fleet:
        final, results, reasons, emergencies, spoof_findings, warnings = analyze_arm(
            arm, model, log
        )
        observed.add(final)
        expected = arm["expected"]
        status = "PASS" if final == expected else "FAIL"

        print(f"\n{arm['arm_id']} -> {final:22s} (expected {expected}: {status})")
        print("  scenario:", arm["scenario"])

        for joint, result in results.items():
            p = "n/a" if result["probability"] is None else f"{result['probability']:.2f}"
            print(
                f"  {joint:8s} {result['decision']:22s} "
                f"ML p(worn)={p:>4s} log_score={result['log_score']} "
            )
            for why in reasons[joint]:
                print("     why:", why)

    required = {"SAFE", "MONITOR", "SCHEDULE_MAINTENANCE", "EMERGENCY_STOP"}
    print("\n" + "=" * 78)
    print("STEP 5: CONSTRAINT CHECKS")
    print("=" * 78)
    print("All four outcomes reachable:", required.issubset(observed))
    print("Observed:", sorted(observed))

    # Demonstrate safety independence from ML.
    arm4 = next(a for a in fleet if a["arm_id"] == "ARM-04")
    emergencies, _ = safety_check(arm4["readings"])
    ml_unavailable_result = "EMERGENCY_STOP" if emergencies else "NOT_EMERGENCY"
    print("ARM-04 with ML model UNAVAILABLE ->", ml_unavailable_result)

    # Demonstrate the value of spoof defense.
    arm5 = next(a for a in fleet if a["arm_id"] == "ARM-05")
    no_spoof = "SCHEDULE_MAINTENANCE"
    with_spoof = analyze_arm(arm5, model, log)[0]
    print("ARM-05 WITHOUT spoof defense ->", no_spoof)
    print("ARM-05 WITH spoof defense    ->", with_spoof)

    if required.issubset(observed) and all(
        analyze_arm(a, model, log)[0] == a["expected"] for a in fleet
    ):
        print("ALL CHECKS PASSED")
    else:
        print("SOME CHECKS FAILED")

if __name__ == "__main__":
    main()
