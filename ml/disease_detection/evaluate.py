from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf
from tensorflow import keras
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

BASE = Path(__file__).resolve().parent
MODEL_DIR = BASE / "models"
OUT = BASE / "eval_output"
OUT.mkdir(exist_ok=True)
IMG_SIZE = 224

with open(MODEL_DIR / "classes.json") as f:
    meta = json.load(f)
class_names = meta["classes"]

model = keras.models.load_model(MODEL_DIR / "cotton_model.keras")

df = pd.read_csv(BASE / "splits.csv")
test_df = df[df["split"] == "test"].reset_index(drop=True)
label_to_id = {c: i for i, c in enumerate(class_names)}
y_true = test_df["label"].map(label_to_id).values


def load_image(path):
    img = tf.io.read_file(str(BASE / path))
    img = tf.io.decode_image(img, channels=3, expand_animations=False)
    img = tf.image.resize(img, (IMG_SIZE, IMG_SIZE))
    return tf.cast(img, tf.float32)


X_test = tf.stack([load_image(p) for p in test_df["path"]])
proba = model.predict(X_test, batch_size=32)
y_pred = proba.argmax(axis=1)

print(f"Test images: {len(test_df)}")
print(f"Test accuracy: {(y_pred == y_true).mean():.4f}")
print(f"ROC-AUC (macro, OvR): {roc_auc_score(y_true, proba, multi_class='ovr', average='macro'):.4f}")

report = classification_report(y_true, y_pred, target_names=class_names, output_dict=True)
report_df = pd.DataFrame(report).T.round(3)
print("\nClass-wise report:\n", report_df.to_string())
report_df.to_csv(OUT / "classwise_report.csv")

cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(9, 7))
sns.heatmap(cm, annot=True, fmt="d", cmap="Greens",
            xticklabels=class_names, yticklabels=class_names)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix (test set)")
plt.tight_layout()
plt.savefig(OUT / "confusion_matrix.png")
plt.close()

# Confidence distribution: khoti predictions nu confidence ocha hoy che ke nahi
conf = proba.max(axis=1)
correct_conf = conf[y_pred == y_true]
wrong_conf = conf[y_pred != y_true]
print(f"\nAvg confidence (correct): {correct_conf.mean():.3f}")
print(f"Avg confidence (wrong):   {wrong_conf.mean():.3f}")

plt.figure(figsize=(7, 5))
plt.hist(correct_conf, bins=20, alpha=0.6, label="correct")
plt.hist(wrong_conf, bins=20, alpha=0.6, label="wrong")
plt.xlabel("Model confidence")
plt.legend()
plt.title("Confidence: correct vs wrong")
plt.savefig(OUT / "confidence_distribution.png")
plt.close()

print("\nSaved in:", OUT)