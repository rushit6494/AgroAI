from pathlib import Path
import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split

BASE = Path(__file__).resolve().parent
DATA = BASE / "dataset" / "sar_cld"
OUT = BASE / "splits.csv"
EXTS = {".jpg", ".jpeg", ".png"}

# Dataset folder name -> clean class name
CLASS_MAP = {
    "Bacterial Blight": "bacterial_blight",
    "Curl Virus": "curl_virus",
    "Healthy Leaf": "healthy",
    "Herbicide Growth Damage": "herbicide_damage",
    "Leaf Hopper Jassids": "leaf_hopper_jassids",
    "Leaf Redding": "leaf_reddening",
    "Leaf Variegation": "leaf_variegation",
}


def is_valid(p: Path) -> bool:
    try:
        with Image.open(p) as im:
            im.verify()
        return True
    except Exception:
        return False


rows, broken = [], 0
for folder in sorted(DATA.iterdir()):
    if not folder.is_dir():
        continue
    if folder.name not in CLASS_MAP:
        print("Unknown folder skipped:", folder.name)
        continue
    for p in folder.rglob("*"):
        if p.suffix.lower() in EXTS:
            if is_valid(p):
                rows.append({"path": str(p.relative_to(BASE)), "label": CLASS_MAP[folder.name]})
            else:
                broken += 1

df = pd.DataFrame(rows)
print("Valid images:", len(df), "| Broken skipped:", broken)

# 70% train, 15% val, 15% test (stratified)
train, temp = train_test_split(df, test_size=0.30, stratify=df["label"], random_state=42)
val, test = train_test_split(temp, test_size=0.50, stratify=temp["label"], random_state=42)

out = pd.concat([
    train.assign(split="train"),
    val.assign(split="val"),
    test.assign(split="test"),
]).reset_index(drop=True)

out.to_csv(OUT, index=False)
print("\nImages per class per split:")
print(out.groupby(["label", "split"]).size().unstack("split")[["train", "val", "test"]])
print("\nSaved:", OUT)