"""Train the 8-class on-device classifier and write Android assets.

The vision folder currently has YOLO labels but no images, so this trains a
small CNN on synthetic class-colored samples that match ScrapClassifier's
float32 224x224 RGB [0, 1] input. Re-run after real photos exist.
"""
from pathlib import Path

import numpy as np
import tensorflow as tf

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "collector_app" / "app" / "src" / "main" / "assets"
LABELS = [
    "Batteries",
    "Copper Cables & Wires",
    "CRT Monitors & TVs",
    "LCD / LED Panels",
    "Mixed E-Waste Plastics",
    "Motors & Magnet Assemblies",
    "Other Electronic Scrap",
    "Printed Circuit Boards (PCBs)",
]
# Distinct RGB means so the demo model is not random on solid-color photos.
MEANS = np.array([
    [0.15, 0.15, 0.18],
    [0.72, 0.38, 0.12],
    [0.22, 0.28, 0.55],
    [0.08, 0.08, 0.10],
    [0.78, 0.18, 0.22],
    [0.45, 0.45, 0.48],
    [0.35, 0.55, 0.25],
    [0.12, 0.55, 0.22],
], dtype=np.float32)


def samples(n_per_class: int) -> tuple[np.ndarray, np.ndarray]:
    images, labels = [], []
    rng = np.random.default_rng(42)
    for i, mean in enumerate(MEANS):
        noise = rng.normal(0, 0.08, (n_per_class, 224, 224, 3)).astype(np.float32)
        batch = np.clip(mean + noise, 0, 1)
        images.append(batch)
        labels.append(np.full(n_per_class, i, dtype=np.int32))
    return np.concatenate(images), np.concatenate(labels)


def build() -> tf.keras.Model:
    return tf.keras.Sequential([
        tf.keras.layers.Input((224, 224, 3)),
        tf.keras.layers.Conv2D(16, 3, strides=2, activation="relu"),
        tf.keras.layers.Conv2D(32, 3, strides=2, activation="relu"),
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(len(LABELS), activation="softmax"),
    ])


def main() -> None:
    x, y = samples(24)
    model = build()
    model.compile(optimizer="adam", loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    model.fit(x, y, epochs=8, batch_size=16, verbose=2)
    converter = tf.lite.TFLiteConverter.from_keras_model(model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    ASSETS.mkdir(parents=True, exist_ok=True)
    (ASSETS / "mobilenet_scrap_v1.tflite").write_bytes(converter.convert())
    (ASSETS / "labels.txt").write_text("\n".join(LABELS) + "\n", encoding="utf-8")
    print("Wrote", ASSETS / "mobilenet_scrap_v1.tflite")


if __name__ == "__main__":
    main()
