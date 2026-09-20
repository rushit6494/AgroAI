from pathlib import Path
import joblib
import pandas as pd

MODEL_PATH = Path(__file__).resolve().parent / "models" / "crop_model.joblib"
_bundle = None


def _load():
    global _bundle
    if _bundle is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError("Model nathi malyu. Pehla train.py chalavo.")
        _bundle = joblib.load(MODEL_PATH)
    return _bundle


def predict_crops(N, P, K, temperature, humidity, ph, rainfall, top_k=3):
    """Top-k crop recommendations return kare (ranked).

    'score' model no relative score che (Random Forest ma trees na vote).
    Te calibrated real probability nathi, etle UI ma 'confidence' tarike
    na batavvu; fakt ranking batavvu.
    """
    if not (0 <= ph <= 14):
        raise ValueError("pH 0 thi 14 vachche hovo joie.")
    if not (0 <= humidity <= 100):
        raise ValueError("Humidity 0 thi 100 vachche hovi joie.")
    if min(N, P, K, rainfall) < 0:
        raise ValueError("N, P, K ane rainfall negative na hoy.")

    b = _load()
    row = pd.DataFrame([[N, P, K, temperature, humidity, ph, rainfall]],
                       columns=b["features"])
    proba = b["model"].predict_proba(row)[0]
    top_idx = proba.argsort()[::-1][:top_k]

    return [
        {"rank": r + 1, "crop": b["label_encoder"].classes_[i], "score": float(proba[i])}
        for r, i in enumerate(top_idx)
    ]


if __name__ == "__main__":
    # Master prompt no example
    result = predict_crops(N=90, P=42, K=43, temperature=25.5,
                           humidity=80, ph=6.5, rainfall=200)
    for r in result:
        print(f"{r['rank']}. {r['crop']}  (score: {r['score']:.2f})")