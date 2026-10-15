import re

STRONG_KEYWORDS = {
    "grinding": 2, "overheat": 2, "overheating": 2,
    "worn": 2, "wear": 2, "rattling": 2
}
MILD_KEYWORDS = {
    "noise": 1, "vibration": 1, "hot": 1,
    "stiff": 1, "unusual": 1, "friction": 1
}
NEGATIONS = {"no", "not", "without", "none", "normal"}

def scan_text(text):
    score, matched = 0, []
    # Clause-level negation: "No unusual noise or vibration" should not
    # become a false warning.
    for clause in re.split(r"[.;,!?]|\bbut\b", text.lower()):
        negated = False
        for word in re.findall(r"[a-z]+", clause):
            if word in NEGATIONS:
                negated = True
                continue
            weight = STRONG_KEYWORDS.get(word, MILD_KEYWORDS.get(word, 0))
            if weight and not negated:
                score += weight
                matched.append(word)
    return score, matched

def scan_log(path, arm_id):
    findings = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|", 2)]
            if len(parts) != 3:
                continue
            date, arm, note = parts
            if arm.upper() != arm_id.upper():
                continue
            score, keywords = scan_text(note)
            if score:
                findings.append({
                    "date": date,
                    "arm": arm,
                    "note": note,
                    "score": score,
                    "keywords": keywords,
                })
    return findings

def joint_log_score(findings, joint):
    score = 0
    keywords = []
    joint_words = {joint.lower()}
    if joint.lower() == "shoulder":
        joint_words |= {"shoulder"}
    elif joint.lower() == "elbow":
        joint_words |= {"elbow"}
    elif joint.lower() == "wrist":
        joint_words |= {"wrist"}

    for item in findings:
        note = item["note"].lower()
        # If a note names a joint, apply it to that joint.
        named_joint = any(j in note for j in ("shoulder", "elbow", "wrist"))
        if named_joint and not any(j in note for j in joint_words):
            continue
        score += item["score"]
        keywords.extend(item["keywords"])
    return score, sorted(set(keywords))
