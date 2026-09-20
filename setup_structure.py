from pathlib import Path

folders = [
    "app/pages", "app/components", "app/services", "app/utils",
    "ml/crop_recommendation/dataset", "ml/crop_recommendation/models",
    "ml/disease_detection/dataset", "ml/disease_detection/models",
    "ml/pest_detection/dataset", "ml/pest_detection/models",
    "ml/soil_analysis",
    "models", "datasets", "database", "treatment_database",
    "uploads", "reports", "notebooks", "tests", "config",
]

files = [
    "app.py", "README.md", "requirements.txt", ".env", ".gitignore",
    "config/settings.py",
    "ml/crop_recommendation/preprocessing.py",
    "ml/crop_recommendation/train.py",
    "ml/crop_recommendation/evaluate.py",
    "ml/crop_recommendation/predict.py",
    "ml/disease_detection/train.py",
    "ml/disease_detection/evaluate.py",
    "ml/disease_detection/predict.py",
    "ml/pest_detection/train.py",
    "ml/pest_detection/evaluate.py",
    "ml/pest_detection/predict.py",
]

for f in folders:
    p = Path(f)
    p.mkdir(parents=True, exist_ok=True)
    (p / ".gitkeep").touch()

for f in files:
    Path(f).touch()

for pkg in ["app", "app/services", "app/utils", "app/components", "config", "ml"]:
    (Path(pkg) / "__init__.py").touch()

print("AgroAI structure ready ✅")