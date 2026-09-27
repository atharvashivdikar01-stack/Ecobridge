package com.ecobridge.ai;

import android.content.Context;
import android.graphics.Bitmap;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import java.util.List;

/**
 * ScrapClassifier
 * Backwards-compatible adapter for on-device scrap classification.
 * Delegates core inference, tensor management, and validation to EwasteClassifier.
 */
public class ScrapClassifier {

    private final EwasteClassifier ewasteClassifier;

    public interface OnClassificationCallback {
        void onResult(ClassificationResult result);
        void onError(Exception e);
    }

    public ScrapClassifier(@NonNull Context context) {
        this.ewasteClassifier = new EwasteClassifier(context);
    }

    public void classifyAsync(@Nullable final Bitmap bitmap, @NonNull final OnClassificationCallback callback) {
        ewasteClassifier.classifyAsync(bitmap, new EwasteClassifier.Callback() {
            @Override
            public void onSuccess(@NonNull PredictionResult result) {
                callback.onResult(ClassificationResult.fromPredictionResult(result));
            }

            @Override
            public void onError(@NonNull Exception e) {
                callback.onError(e);
            }
        });
    }

    @NonNull
    public ClassificationResult classify(@Nullable Bitmap bitmap) {
        PredictionResult prediction = ewasteClassifier.classify(bitmap);
        return ClassificationResult.fromPredictionResult(prediction);
    }

    public List<String> getCategories() {
        return ewasteClassifier.getCategories();
    }

    public EwasteClassifier getEwasteClassifier() {
        return ewasteClassifier;
    }

    public void close() {
        ewasteClassifier.close();
    }
}
