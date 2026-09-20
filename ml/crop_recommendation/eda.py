from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

BASE = Path(__file__).resolve().parent
DATA = BASE / "dataset" / "Crop_recommendation.csv"
OUT = BASE / "eda_output"
OUT.mkdir(exist_ok=True)

df = pd.read_csv(DATA)

print("Shape:", df.shape)
print("\nColumns:", list(df.columns))
print("\nMissing values:\n", df.isnull().sum())
print("\nDuplicates:", df.duplicated().sum())
print("\nDescribe:\n", df.describe().round(2))
print("\nClasses:", df["label"].nunique())
print(df["label"].value_counts())

# 1. Class distribution
plt.figure(figsize=(10, 6))
df["label"].value_counts().plot(kind="barh")
plt.title("Crop class distribution")
plt.tight_layout()
plt.savefig(OUT / "class_distribution.png")
plt.close()

# 2. Correlation heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(df.drop(columns="label").corr(), annot=True, cmap="YlGn", fmt=".2f")
plt.title("Feature correlation")
plt.tight_layout()
plt.savefig(OUT / "correlation.png")
plt.close()

# 3. Feature distributions
features = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
df[features].hist(bins=25, figsize=(12, 8), color="seagreen")
plt.tight_layout()
plt.savefig(OUT / "feature_distributions.png")
plt.close()

print("\nEDA charts saved in:", OUT)