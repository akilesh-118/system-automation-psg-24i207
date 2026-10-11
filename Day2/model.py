
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
    

DATA_FILE = Path(__file__).parent / "data" / "day2_sample_.csv"

FEATURES = [
    "temperature",
    "pressure",
    "vibration",
    "rpm",
    "current"
]
def train_data():
    df = pd.read_csv(DATA_FILE)
    required_columns = FEATURES + ["state"]
    if not all(column in df.columns for column in required_columns):
        raise ValueError("CSV is missing required columns.")
    
    if df[required_columns].isnull().any().any():
        raise ValueError("CSV contains missing values.")
    
    X = df[FEATURES]
    y = df["state"]
    X_train, X_test, y_train, y_test = train_test_split(X,y,test_size=0.25,random_state=42,stratify=y)

    model = RandomForestClassifier(n_estimators=200,max_depth=8,class_weight="balanced",random_state=42)

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(f"\nModel trained. Holdout accuracy: {accuracy * 100:.2f}%")
    return model
if __name__ == "__main__":
    trained_model = train_data()
    sample_reading = pd.DataFrame([[75.0, 1000.0, 1.2, 3500.0, 15.0]],columns=FEATURES)
    prediction = trained_model.predict(sample_reading)[0]
    print("\nSample live reading:")
    print(sample_reading.to_dict(orient="records")[0])
    print("Model prediction:", prediction)
