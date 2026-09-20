from pathlib import Path
import joblib
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from xgboost import XGBClassifier

from preprocessing import prepare_data, FEATURES

BASE = Path(__file__).resolve().parent
MODEL_DIR = BASE / "models"
MODEL_DIR.mkdir(exist_ok=True)

X_train, X_test, y_train, y_test, le = prepare_data()
print(f"Train: {X_train.shape}, Test: {X_test.shape}, Classes: {len(le.classes_)}")

models = {
    "Decision Tree": DecisionTreeClassifier(random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
    "KNN": Pipeline([("scaler", StandardScaler()), ("clf", KNeighborsClassifier(n_neighbors=5))]),
    "SVM": Pipeline([("scaler", StandardScaler()), ("clf", SVC(kernel="rbf", probability=True, random_state=42))]),
    "XGBoost": XGBClassifier(eval_metric="mlogloss", random_state=42, n_jobs=-1),
}

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
rows = []

for name, model in models.items():
    print(f"\nTraining: {name} ...")

    # Model selection: fakt TRAIN data par cross-validation
    cv = cross_validate(
        model, X_train, y_train, cv=skf,
        scoring={"acc": "accuracy", "f1": "f1_macro"}, n_jobs=-1,
    )

    # Final report mate: test set par
    model.fit(X_train, y_train)
    pred = model.predict(X_test)

    rows.append({
        "model": name,
        "cv_accuracy": cv["test_acc"].mean(),
        "cv_f1_macro": cv["test_f1"].mean(),
        "test_accuracy": accuracy_score(y_test, pred),
        "test_precision": precision_score(y_test, pred, average="macro"),
        "test_recall": recall_score(y_test, pred, average="macro"),
        "test_f1": f1_score(y_test, pred, average="macro"),
    })

results = pd.DataFrame(rows).sort_values("cv_f1_macro", ascending=False).round(4)
print("\n===== MODEL COMPARISON =====")
print(results.to_string(index=False))
results.to_csv(MODEL_DIR / "model_comparison.csv", index=False)

# Best model: CV F1 (macro) par thi, test set par thi nahi
best_name = results.iloc[0]["model"]
best_model = models[best_name]
print(f"\nBest model: {best_name}")

joblib.dump(
    {
        "model": best_model,
        "label_encoder": le,
        "features": FEATURES,
        "model_name": best_name,
    },
    MODEL_DIR / "crop_model.joblib",
)
print("Saved:", MODEL_DIR / "crop_model.joblib")