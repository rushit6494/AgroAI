from pathlib import Path
from pathlib import Path
import sys

# Project root ne path ma umero, jethi "config" module malse
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from config.settings import DISEASE_CONFIDENCE_THRESHOLD
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from config.settings import DISEASE_CONFIDENCE_THRESHOLD

BASE = Path(__file__).resolve().parent
MODEL_DIR = BASE / "models"
IMG_SIZE = 224

# Class -> (praakar, farmer ne batavva mate naam)
CLASS_INFO = {
    "bacterial_blight": ("disease", "Bacterial Blight"),
    "curl_virus": ("disease", "Cotton Leaf Curl Virus"),
    "healthy": ("healthy", "Healthy"),
    "herbicide_damage": ("physical_damage", "Herbicide Growth Damage"),
    "leaf_hopper_jassids": ("pest", "Leaf Hopper / Jassid Damage"),
    "leaf_reddening": ("unknown_cause", "Leaf Reddening"),
    "leaf_variegation": ("unknown_cause", "Leaf Variegation"),
}

_model = None
_classes = None


def _load():
    global _model, _classes
    if _model is None:
        with open(MODEL_DIR / "classes.json") as f:
            _classes = json.load(f)["classes"]
        _model = keras.models.load_model(MODEL_DIR / "cotton_model.keras")
    return _model, _classes


def predict_disease(image_path, top_k=3):
    model, classes = _load()

    img = tf.io.read_file(str(image_path))
    img = tf.io.decode_image(img, channels=3, expand_animations=False)
    img = tf.image.resize(img, (IMG_SIZE, IMG_SIZE))
    img = tf.cast(img, tf.float32)[None, ...]

    proba = model.predict(img, verbose=0)[0]
    top_idx = proba.argsort()[::-1][:top_k]

    predictions = [
        {"class": classes[i], "label": CLASS_INFO[classes[i]][1],
         "type": CLASS_INFO[classes[i]][0], "confidence": float(proba[i])}
        for i in top_idx
    ]
    top = predictions[0]

    result = {
        "crop": "Cotton",
        "predictions": predictions,
        "top_prediction": top,
        "confident": top["confidence"] >= DISEASE_CONFIDENCE_THRESHOLD,
        "severity": "Unknown",  # dataset ma severity data nathi
    }

    if not result["confident"]:
        result["message"] = (
            "⚠️ Analysis Uncertain. Please upload a clearer image showing the "
            "entire plant, the affected leaf, and a close-up of the affected area."
        )
    elif top["type"] == "unknown_cause":
        result["message"] = (
            f"{top['label']} visually detected, but the exact cause (nutrient "
            "deficiency, stress, or disease) cannot be determined from this image. "
            "Please consult a local agricultural expert."
        )
    elif top["type"] == "healthy":
        result["message"] = "Plant looks healthy. No visible disease or pest damage detected."
    else:
        result["message"] = (
            f"Possible issue detected: {top['label']} "
            f"({top['type'].replace('_', ' ')}, confidence {top['confidence']:.0%})."
        )

    return result


if __name__ == "__main__":
    import pandas as pd
    df = pd.read_csv(BASE / "splits.csv")
    sample = df[df["split"] == "test"].sample(1, random_state=1).iloc[0]
    print("Actual label:", sample["label"])
    result = predict_disease(BASE / sample["path"])
    for p in result["predictions"]:
        print(f"  {p['label']}: {p['confidence']:.2f}")
    print("\n", result["message"])