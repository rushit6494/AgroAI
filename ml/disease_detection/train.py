from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.utils.class_weight import compute_class_weight

BASE = Path(__file__).resolve().parent
MODEL_DIR = BASE / "models"
MODEL_DIR.mkdir(exist_ok=True)
MODEL_PATH = MODEL_DIR / "cotton_model.keras"

IMG_SIZE = 224
BATCH = 32
SEED = 42
keras.utils.set_random_seed(SEED)

# ---------- Data ----------
df = pd.read_csv(BASE / "splits.csv")
class_names = sorted(df["label"].unique())
label_to_id = {c: i for i, c in enumerate(class_names)}
df["y"] = df["label"].map(label_to_id)
df["full_path"] = df["path"].apply(lambda p: str(BASE / p))
print("Classes:", class_names)


def load_image(path, label):
    img = tf.io.read_file(path)
    img = tf.io.decode_image(img, channels=3, expand_animations=False)
    img = tf.image.resize(img, (IMG_SIZE, IMG_SIZE))
    img = tf.cast(tf.round(img), tf.uint8)  # cache nano rakhva
    img.set_shape([IMG_SIZE, IMG_SIZE, 3])
    return img, label


def make_ds(split, training=False):
    d = df[df["split"] == split]
    ds = tf.data.Dataset.from_tensor_slices((d["full_path"].values, d["y"].values))
    ds = ds.map(load_image, num_parallel_calls=tf.data.AUTOTUNE).cache()
    if training:
        ds = ds.shuffle(len(d), seed=SEED)
    ds = ds.batch(BATCH).map(lambda x, y: (tf.cast(x, tf.float32), y))
    return ds.prefetch(tf.data.AUTOTUNE)


train_ds = make_ds("train", training=True)
val_ds = make_ds("val")

# Imbalance mate class weights
train_y = df[df["split"] == "train"]["y"].values
w = compute_class_weight("balanced", classes=np.arange(len(class_names)), y=train_y)
class_weight = dict(enumerate(w))
print("Class weights:", {class_names[i]: round(v, 2) for i, v in class_weight.items()})

# ---------- Model ----------
# Augmentation: color/hue badalvu nahi, kem ke leaf reddening ane variegation
# color par aadharit che. Fakt halka geometry ane brightness badlav.
augment = keras.Sequential([
    layers.RandomFlip("horizontal"),
    layers.RandomRotation(0.05),
    layers.RandomZoom(0.1),
    layers.RandomTranslation(0.05, 0.05),
    layers.RandomBrightness(0.1, value_range=(0, 255)),
], name="augmentation")

base = keras.applications.MobileNetV2(
    input_shape=(IMG_SIZE, IMG_SIZE, 3), include_top=False, weights="imagenet"
)
base.trainable = False

inputs = keras.Input(shape=(IMG_SIZE, IMG_SIZE, 3))
x = augment(inputs)
x = layers.Rescaling(1 / 127.5, offset=-1)(x)  # MobileNetV2 preprocessing
x = base(x, training=False)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dropout(0.3)(x)
outputs = layers.Dense(len(class_names), activation="softmax")(x)
model = keras.Model(inputs, outputs)

# ---------- Stage 1: fakt navo head train ----------
model.compile(
    optimizer=keras.optimizers.Adam(1e-3),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)
cb1 = [
    keras.callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True),
    keras.callbacks.ModelCheckpoint(MODEL_PATH, monitor="val_loss", save_best_only=True),
]
print("\n=== Stage 1: head training ===")
h1 = model.fit(train_ds, validation_data=val_ds, epochs=15,
               class_weight=class_weight, callbacks=cb1)
best_val = min(h1.history["val_loss"])

# ---------- Stage 2: fine-tuning ----------
base.trainable = True
for layer in base.layers[:-30]:
    layer.trainable = False
for layer in base.layers:
    if isinstance(layer, layers.BatchNormalization):
        layer.trainable = False

model.compile(
    optimizer=keras.optimizers.Adam(1e-5),
    loss="sparse_categorical_crossentropy",
    metrics=["accuracy"],
)
cb2 = [
    keras.callbacks.EarlyStopping(monitor="val_loss", patience=4, restore_best_weights=True),
    keras.callbacks.ModelCheckpoint(MODEL_PATH, monitor="val_loss", save_best_only=True,
                                    initial_value_threshold=best_val),
]
print("\n=== Stage 2: fine-tuning ===")
h2 = model.fit(train_ds, validation_data=val_ds, epochs=10,
               class_weight=class_weight, callbacks=cb2)

# ---------- Save ----------
with open(MODEL_DIR / "classes.json", "w") as f:
    json.dump({"classes": class_names, "img_size": IMG_SIZE}, f, indent=2)

acc = h1.history["accuracy"] + h2.history["accuracy"]
val_acc = h1.history["val_accuracy"] + h2.history["val_accuracy"]
plt.figure(figsize=(8, 5))
plt.plot(acc, label="train acc")
plt.plot(val_acc, label="val acc")
plt.axvline(len(h1.history["accuracy"]) - 1, color="gray", linestyle="--", label="fine-tune start")
plt.legend()
plt.title("Training curves")
plt.savefig(MODEL_DIR / "training_curves.png")

print("\nBest model saved:", MODEL_PATH)
