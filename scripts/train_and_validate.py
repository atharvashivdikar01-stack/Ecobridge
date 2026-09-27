import os
import pathlib
import shutil
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

def main():
    root = pathlib.Path("datasets/ai_ml/vision")
    train_dir = root / "train_classes"
    val_dir = root / "val_classes"

    image_size = (224, 224)
    batch_size = 8

    # Set random seeds for reproducibility
    tf.random.set_seed(42)
    np.random.seed(42)

    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        image_size=image_size,
        batch_size=batch_size,
        label_mode='int',
        shuffle=True,
        seed=42
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        val_dir,
        image_size=image_size,
        batch_size=batch_size,
        label_mode='int',
        shuffle=False
    )

    labels = train_ds.class_names
    print(f"Discovered {len(labels)} classes: {labels}")
    assert labels == ['BATTERIES', 'CABLES', 'CRT', 'LCD_LED_PANEL', 'MIXED_PLASTICS', 'MOTORS_MAGNETS', 'OTHER_EWASTE', 'PCB'], f"Unexpected labels: {labels}"

    label_map = {
        'BATTERIES': 'Batteries',
        'CABLES': 'Copper Cables & Wires',
        'CRT': 'CRT Monitors & TVs',
        'LCD_LED_PANEL': 'LCD / LED Panels',
        'MIXED_PLASTICS': 'Mixed E-Waste Plastics',
        'MOTORS_MAGNETS': 'Motors & Magnet Assemblies',
        'OTHER_EWASTE': 'Other Electronic Scrap',
        'PCB': 'Printed Circuit Boards (PCBs)'
    }

    friendly_labels = [label_map[l] for l in labels]

    augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip('horizontal'),
        tf.keras.layers.RandomRotation(0.08),
        tf.keras.layers.RandomContrast(0.1)
    ], name="augmentation")

    base = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet'
    )
    base.trainable = False

    # Note: Keras MobileNetV2 preprocess_input takes [0, 255] and converts to [-1, 1]
    inputs = tf.keras.Input(shape=(224, 224, 3), name="input_image")
    x = augmentation(inputs)
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
    x = base(x, training=False)
    x = tf.keras.layers.GlobalAveragePooling2D(name="avg_pool")(x)
    x = tf.keras.layers.Dropout(0.2, name="dropout")(x)
    outputs = tf.keras.layers.Dense(len(labels), activation='softmax', name="predictions")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="mobilenet_scrap_v1")

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    print("\n--- Training Model ---")
    model.fit(
        train_ds.prefetch(tf.data.AUTOTUNE),
        validation_data=val_ds.prefetch(tf.data.AUTOTUNE),
        epochs=30,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(patience=8, restore_best_weights=True, monitor='val_accuracy')
        ]
    )

    print("\n--- Converting to TFLite (matches Colab export) ---")
    # For inference, remove data augmentation so inference graph is clean
    inference_inputs = tf.keras.Input(shape=(224, 224, 3), name="input_image")
    inf_x = tf.keras.applications.mobilenet_v2.preprocess_input(inference_inputs)
    inf_x = base(inf_x, training=False)
    inf_x = model.get_layer("avg_pool")(inf_x)
    # dense layer weights from trained model
    inf_out = model.get_layer("predictions")(inf_x)
    inference_model = tf.keras.Model(inputs=inference_inputs, outputs=inf_out, name="mobilenet_scrap_v1_inference")

    converter = tf.lite.TFLiteConverter.from_keras_model(inference_model)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

    output_tflite_path = "collector_app/app/src/main/assets/mobilenet_scrap_v1.tflite"
    output_labels_path = "collector_app/app/src/main/assets/labels.txt"

    with open(output_tflite_path, "wb") as f:
        f.write(tflite_model)
    print(f"Saved TFLite model to {output_tflite_path} (size: {len(tflite_model)} bytes, {len(tflite_model)/(1024*1024):.2f} MB)")

    with open(output_labels_path, "w") as f:
        f.write("\n".join(friendly_labels) + "\n")
    print(f"Saved labels to {output_labels_path}")

    # Also save a copy in ai/ directory for reference
    with open("ai/mobilenet_scrap_v1.tflite", "wb") as f:
        f.write(tflite_model)
    with open("ai/labels.txt", "w") as f:
        f.write("\n".join(friendly_labels) + "\n")

    print("\n--- Validating TFLite Model on Validation Set ---")
    interpreter = tf.lite.Interpreter(model_path=output_tflite_path)
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print(f"TFLite Input Details: Shape={input_details[0]['shape']}, Dtype={input_details[0]['dtype']}")
    print(f"TFLite Output Details: Shape={output_details[0]['shape']}, Dtype={output_details[0]['dtype']}")

    y_true = []
    y_pred = []
    y_conf = []

    for images, batch_labels in val_ds:
        for img, lbl in zip(images.numpy(), batch_labels.numpy()):
            # img has shape (224, 224, 3), range [0, 255] float32
            input_tensor = np.expand_dims(img.astype(np.float32), axis=0)
            interpreter.set_tensor(input_details[0]['index'], input_tensor)
            interpreter.invoke()
            output = interpreter.get_tensor(output_details[0]['index'])[0]
            pred_idx = np.argmax(output)
            confidence = output[pred_idx]

            y_true.append(lbl)
            y_pred.append(pred_idx)
            y_conf.append(confidence)

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    accuracy = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
    cm = confusion_matrix(y_true, y_pred, labels=list(range(len(labels))))

    print("\n================ VALIDATION REPORT ================")
    print(f"Accuracy:  {accuracy * 100:.2f}%")
    print(f"Precision: {precision * 100:.2f}%")
    print(f"Recall:    {recall * 100:.2f}%")
    print(f"F1-score:  {f1 * 100:.2f}%")
    print("\nConfusion Matrix:")
    print(cm)
    print("\nClassification Report (Per-Class Performance):")
    print(classification_report(y_true, y_pred, target_names=friendly_labels, zero_division=0))
    print("===================================================\n")

if __name__ == "__main__":
    main()
