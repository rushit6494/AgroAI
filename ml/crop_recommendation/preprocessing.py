from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

BASE = Path(__file__).resolve().parent
FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TARGET = "label"


def load_data() -> pd.DataFrame:
    csv_files = list((BASE / "dataset").glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("dataset folder ma CSV nathi.")
    df = pd.read_csv(csv_files[0])
    df = df.drop_duplicates().dropna()
    return df


def prepare_data(test_size=0.2, random_state=42):
    """Train/test split (stratified) + label encoding."""
    df = load_data()
    X = df[FEATURES]
    le = LabelEncoder()
    y = le.fit_transform(df[TARGET])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=random_state
    )
    return X_train, X_test, y_train, y_test, le