package com.ecobridge.ai;

import android.content.Context;
import android.content.res.AssetFileDescriptor;
import android.graphics.Bitmap;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.ecobridge.ai.deepscan.DefaultSafetyAnalyzer;
import com.ecobridge.ai.deepscan.SafetyAnalyzer;

import org.tensorflow.lite.Interpreter;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.MappedByteBuffer;
import java.nio.channels.FileChannel;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * EwasteClassifier
 * High-performance, offline-first on-device scrap material classifier.
 * Executes quantized/optimized MobileNetV2 TensorFlow Lite inference,
 * producing multi-class probabilities, confidence thresholds, and hazard warnings.
 */
public class EwasteClassifier {

    private static final String TAG = "EwasteClassifier";

    public static final String MODEL_FILE = "mobilenet_scrap_v1.tflite";
    public static final String LABELS_FILE = "labels.txt";
    public static final String MODEL_VERSION = "mobilenet_scrap_v1";

    public static final int INPUT_IMAGE_SIZE = 224;
    public static final int PIXEL_SIZE = 3; // RGB
    public static final float DEFAULT_CONFIDENCE_THRESHOLD = 0.50f;

    private final Context context;
    private final SafetyAnalyzer safetyAnalyzer;
    private final ExecutorService executorService;
    private final Handler mainHandler;

    private Interpreter tfliteInterpreter;
    private final List<String> categories = new ArrayList<>();
    private boolean isModelLoaded = false;
    private float confidenceThreshold = DEFAULT_CONFIDENCE_THRESHOLD;

    public interface Callback {
        void onSuccess(@NonNull PredictionResult result);
        void onError(@NonNull Exception e);
    }

    public EwasteClassifier(@NonNull Context context) {
        this(context, new DefaultSafetyAnalyzer(), DEFAULT_CONFIDENCE_THRESHOLD);
    }

    public EwasteClassifier(@NonNull Context context,
                            @NonNull SafetyAnalyzer safetyAnalyzer,
                            float confidenceThreshold) {
        this.context = context.getApplicationContext();
        this.safetyAnalyzer = safetyAnalyzer;
        this.confidenceThreshold = confidenceThreshold;
        this.executorService = Executors.newSingleThreadExecutor();
        this.mainHandler = new Handler(Looper.getMainLooper());

        loadLabels();
        initInterpreter();
    }

    private void loadLabels() {
        categories.clear();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(context.getAssets().open(LABELS_FILE)))) {
            String line;
            while ((line = reader.readLine()) != null) {
                line = line.trim();
                if (!line.isEmpty()) {
                    categories.add(line);
                }
            }
            Log.i(TAG, "Successfully loaded " + categories.size() + " categories from " + LABELS_FILE);
        } catch (IOException e) {
            Log.w(TAG, "Failed reading " + LABELS_FILE + " from assets. Falling back to default 8-class catalog.", e);
            categories.clear();
            categories.add("Batteries");
            categories.add("Copper Cables & Wires");
            categories.add("CRT Monitors & TVs");
            categories.add("LCD / LED Panels");
            categories.add("Mixed E-Waste Plastics");
            categories.add("Motors & Magnet Assemblies");
            categories.add("Other Electronic Scrap");
            categories.add("Printed Circuit Boards (PCBs)");
        }
    }

    private synchronized void initInterpreter() {
        try {
            MappedByteBuffer buffer = loadModelBuffer(MODEL_FILE);
            Interpreter.Options options = new Interpreter.Options();
            options.setNumThreads(Math.max(2, Runtime.getRuntime().availableProcessors() / 2));
            options.setUseXNNPACK(true);
            tfliteInterpreter = new Interpreter(buffer, options);
            isModelLoaded = true;
            Log.i(TAG, "TFLite model [" + MODEL_VERSION + "] initialized successfully.");
        } catch (Exception e) {
            Log.e(TAG, "Failed to initialize TFLite model from assets/" + MODEL_FILE + ": " + e.getMessage());
            isModelLoaded = false;
            tfliteInterpreter = null;
        }
    }

    private MappedByteBuffer loadModelBuffer(String modelPath) throws IOException {
        AssetFileDescriptor fileDescriptor = context.getAssets().openFd(modelPath);
        try (FileInputStream inputStream = new FileInputStream(fileDescriptor.getFileDescriptor())) {
            FileChannel fileChannel = inputStream.getChannel();
            long startOffset = fileDescriptor.getStartOffset();
            long declaredLength = fileDescriptor.getDeclaredLength();
            return fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength);
        }
    }

    /**
     * Executes classification asynchronously off the UI thread and returns results on the main thread.
     */
    public void classifyAsync(@Nullable final Bitmap bitmap, @NonNull final Callback callback) {
        executorService.execute(() -> {
            try {
                final PredictionResult result = classify(bitmap);
                mainHandler.post(() -> callback.onSuccess(result));
            } catch (final Exception e) {
                Log.e(TAG, "Uncaught error during classification: " + e.getMessage(), e);
                mainHandler.post(() -> callback.onError(e));
            }
        });
    }

    /**
     * Synchronous classification. Thread-safe.
     */
    @NonNull
    public synchronized PredictionResult classify(@Nullable Bitmap bitmap) {
        if (bitmap == null) {
            return PredictionResult.createFallback(
                    "Unable to analyze image. Please capture another image.",
                    PredictionResult.Status.INVALID_IMAGE
            );
        }

        if (!isModelLoaded || tfliteInterpreter == null) {
            Log.w(TAG, "Classifier invoked while model is not loaded. Returning manual fallback.");
            return PredictionResult.createFallback(
                    "AI model unavailable. Please select the category manually.",
                    PredictionResult.Status.MODEL_UNAVAILABLE
            );
        }

        long startTime = SystemClock.uptimeMillis();

        try {
            ByteBuffer inputBuffer = convertBitmapToByteBuffer(bitmap);
            float[][] outputScores = new float[1][categories.size()];

            tfliteInterpreter.run(inputBuffer, outputScores);

            long inferenceTimeMs = SystemClock.uptimeMillis() - startTime;
            Log.i(TAG, String.format(
                    "Inference time: %d ms | Model: %s | Input: %dx%d",
                    inferenceTimeMs, MODEL_VERSION, INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE
            ));

            float[] scores = outputScores[0];
            List<CategoryPrediction> ranked = new ArrayList<>();
            for (int i = 0; i < scores.length && i < categories.size(); i++) {
                ranked.add(new CategoryPrediction(categories.get(i), scores[i], 0));
            }

            // Sort descending by score
            Collections.sort(ranked, (a, b) -> Float.compare(b.getConfidence(), a.getConfidence()));

            // Assign ranks to top 3
            List<CategoryPrediction> topPredictions = new ArrayList<>();
            for (int i = 0; i < Math.min(3, ranked.size()); i++) {
                CategoryPrediction orig = ranked.get(i);
                topPredictions.add(new CategoryPrediction(orig.getCategory(), orig.getConfidence(), i + 1));
            }

            CategoryPrediction top1 = ranked.get(0);
            String bestCategory = top1.getCategory();
            float bestConfidence = top1.getConfidence();

            boolean isLowConfidence = bestConfidence < confidenceThreshold;
            PredictionResult.Status status = isLowConfidence
                    ? PredictionResult.Status.LOW_CONFIDENCE
                    : PredictionResult.Status.SUCCESS;

            SafetyAnalyzer.HazardAssessment hazard = safetyAnalyzer.assessSafety(bestCategory, bestConfidence);

            return new PredictionResult(
                    bestCategory,
                    bestConfidence,
                    topPredictions,
                    hazard.isHazardous(),
                    hazard.getHazardWarning(),
                    isLowConfidence,
                    MODEL_VERSION,
                    inferenceTimeMs,
                    status,
                    isLowConfidence ? "AI could not confidently identify this item. Please confirm manually." : ""
            );
        } catch (Exception e) {
            Log.e(TAG, "TFLite inference runtime failure: " + e.getMessage(), e);
            return PredictionResult.createFallback(
                    "Inference failed. Please select the category manually.",
                    PredictionResult.Status.ERROR
            );
        }
    }

    /**
     * Converts Bitmap to direct ByteBuffer with exact training normalization.
     * Note: MobileNetV2 preprocess_input layer inside the converted TFLite model expects
     * raw RGB float values in [0.0f, 255.0f].
     */
    private ByteBuffer convertBitmapToByteBuffer(Bitmap bitmap) {
        Bitmap resizedBitmap = Bitmap.createScaledBitmap(bitmap, INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE, true);
        ByteBuffer byteBuffer = ByteBuffer.allocateDirect(4 * INPUT_IMAGE_SIZE * INPUT_IMAGE_SIZE * PIXEL_SIZE);
        byteBuffer.order(ByteOrder.nativeOrder());

        int[] intValues = new int[INPUT_IMAGE_SIZE * INPUT_IMAGE_SIZE];
        resizedBitmap.getPixels(intValues, 0, resizedBitmap.getWidth(), 0, 0, resizedBitmap.getWidth(), resizedBitmap.getHeight());

        int pixel = 0;
        for (int i = 0; i < INPUT_IMAGE_SIZE; ++i) {
            for (int j = 0; j < INPUT_IMAGE_SIZE; ++j) {
                final int val = intValues[pixel++];
                // Feed raw RGB float [0.0, 255.0] matching model's embedded preprocess_input layer
                byteBuffer.putFloat((val >> 16) & 0xFF);
                byteBuffer.putFloat((val >> 8) & 0xFF);
                byteBuffer.putFloat(val & 0xFF);
            }
        }
        return byteBuffer;
    }

    public List<String> getCategories() {
        return new ArrayList<>(categories);
    }

    public boolean isModelLoaded() {
        return isModelLoaded;
    }

    public float getConfidenceThreshold() {
        return confidenceThreshold;
    }

    public void setConfidenceThreshold(float confidenceThreshold) {
        this.confidenceThreshold = confidenceThreshold;
    }

    public synchronized void close() {
        if (tfliteInterpreter != null) {
            try {
                tfliteInterpreter.close();
            } catch (Exception ignored) {}
            tfliteInterpreter = null;
        }
        isModelLoaded = false;
        executorService.shutdown();
    }
}
