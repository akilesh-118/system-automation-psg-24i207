import csv
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import accuracy_score, confusion_matrix

from config import TORQUE_EMERGENCY_NM

def features(row):
    return [
        float(row["torque_nm"]) / TORQUE_EMERGENCY_NM * 100.0,
        float(row["temperature_c"]),
        float(row["vibration_mms"]),
    ]

def load_dataset(path):
    X, y = [], []
    with Path(path).open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            X.append(features(row))
            y.append(int(row["wear_label"]))
    return X, y

def train_model(path, seed=42):
    X, y = load_dataset(path)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=seed, stratify=y
    )

    model = DecisionTreeClassifier(
        max_depth=3,
        min_samples_leaf=5,
        random_state=seed
    )
    model.fit(X_train, y_train)

    train_acc = accuracy_score(y_train, model.predict(X_train))
    test_acc = accuracy_score(y_test, model.predict(X_test))
    cm = confusion_matrix(y_test, model.predict(X_test), labels=[0, 1])

    return model, {
        "rows": len(X),
        "train_rows": len(X_train),
        "test_rows": len(X_test),
        "train_accuracy": train_acc,
        "test_accuracy": test_acc,
        "confusion_matrix": cm.tolist(),
        "tree_rules": export_text(
            model,
            feature_names=["torque_pct_of_limit", "temperature_c", "vibration_mms"]
        ),
    }

def predict_joint(model, reading):
    if any(reading.get(k) is None for k in ("torque", "temperature", "vibration")):
        return None
    x = [[
        reading["torque"] / TORQUE_EMERGENCY_NM * 100.0,
        reading["temperature"],
        reading["vibration"],
    ]]
    probability = float(model.predict_proba(x)[0][1])
    label = int(model.predict(x)[0])
    return label, probability
