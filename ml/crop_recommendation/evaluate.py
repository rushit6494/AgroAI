from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, accuracy_score
)

from preprocessing import prepare_data

BASE = Path(__file__).resolve().parent
OUT = BASE / "eval_output"
OUT.mkdir(exist_ok=True)

bundle = joblib.load(BASE / "models" / "crop_model.joblib")
model, le, features = bundle["model"], bundle["label_encoder"], bundle["features"]

# Same random_state => same test set jem train ma hato
_, X_test, _, y_test, _ = prepare_data()

pred = model.predict(X_test)
proba = model.predict_proba(X_test)

print(f"Model: {bundle['model_name']}")
print(f"Test accuracy: {accuracy_score(y_test, pred):.4f}")
print(f"ROC-AUC (macro, OvR): {roc_auc_score(y_test, proba, multi_class='ovr', average='macro'):.4f}")

# Class-wise report
report = classification_report(y_test, pred, target_names=le.classes_, output_dict=True)
report_df = pd.DataFrame(report).T.round(3)
print("\nClass-wise report:\n", report_df.to_string())
report_df.to_csv(OUT / "classwise_report.csv")

# Confusion matrix
cm = confusion_matrix(y_test, pred)
plt.figure(figsize=(12, 10))
sns.heatmap(cm, annot=True, fmt="d", cmap="Greens",
            xticklabels=le.classes_, yticklabels=le.classes_)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.tight_layout()
plt.savefig(OUT / "confusion_matrix.png")
plt.close()

# Galat predictions
wrong = np.where(pred != y_test)[0]
print(f"\nMisclassified: {len(wrong)} / {len(y_test)}")
for i in wrong:
    print(f"  actual={le.classes_[y_test[i]]}, predicted={le.classes_[pred[i]]}")

# Feature importance (Random Forest / XGBoost / Decision Tree mate)
if hasattr(model, "feature_importances_"):
    imp = pd.Series(model.feature_importances_, index=features).sort_values()
    plt.figure(figsize=(8, 5))
    imp.plot(kind="barh", color="seagreen")
    plt.title("Feature Importance")
    plt.tight_layout()
    plt.savefig(OUT / "feature_importance.png")
    plt.close()
    print("\nFeature importance:\n", imp.sort_values(ascending=False).round(3))

print("\nSaved in:", OUT)