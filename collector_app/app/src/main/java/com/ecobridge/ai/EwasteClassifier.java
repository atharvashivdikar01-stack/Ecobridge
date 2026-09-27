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
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
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

    private static volatile EwasteClassifier sInstance;

    private final Context context;
    private final SafetyAnalyzer safetyAnalyzer;
    private final ExecutorService executorService;
    private final Handler mainHandler;

    private Interpreter tfliteInterpreter;
    private AssetFileDescriptor activeModelAfd;
    private FileInputStream activeFis;
    private final List<String> categories = new ArrayList<>();
    private boolean isModelLoaded = false;
    private String modelInitError = null;
    private float confidenceThreshold = DEFAULT_CONFIDENCE_THRESHOLD;

    public interface Callback {
        void onSuccess(@NonNull PredictionResult result);
        void onError(@NonNull Exception e);
    }

    public static EwasteClassifier getInstance(@NonNull Context context) {
        if (sInstance == null) {
            synchronized (EwasteClassifier.class) {
                if (sInstance == null) {
                    sInstance = new EwasteClassifier(context.getApplicationContext());
                }
            }
        }
        return sInstance;
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
        ByteBuffer buffer = null;
        Throwable lastError = null;

        try {
            buffer = loadModelBuffer(MODEL_FILE);
        } catch (Throwable t) {
            Log.e(TAG, "Failed loading buffer for " + MODEL_FILE, t);
            lastError = t;
        }

        if (buffer == null) {
            isModelLoaded = false;
            tfliteInterpreter = null;
            modelInitError = lastError != null ? lastError.getClass().getSimpleName() + ": " + lastError.getMessage() : "Model buffer null";
            Log.e(TAG, "Cannot initialize TFLite interpreter: " + modelInitError);
            return;
        }

        // Tier 1: Try with multi-threaded options and XNNPACK delegate
        try {
            Interpreter.Options options = new Interpreter.Options();
            options.setNumThreads(Math.min(4, Math.max(2, Runtime.getRuntime().availableProcessors() / 2)));
            try {
                options.setUseXNNPACK(true);
            } catch (Throwable ignored) {}
            tfliteInterpreter = new Interpreter(buffer, options);
            isModelLoaded = true;
            modelInitError = null;
            Log.i(TAG, "TFLite model [" + MODEL_VERSION + "] initialized successfully with XNNPACK.");
            return;
        } catch (Throwable t1) {
            Log.w(TAG, "Interpreter init with XNNPACK failed: " + t1.getMessage() + ". Retrying without XNNPACK...", t1);
            lastError = t1;
        }

        // Tier 2: Pure CPU Interpreter (no XNNPACK, 2 threads)
        try {
            buffer.rewind();
            Interpreter.Options cpuOptions = new Interpreter.Options();
            cpuOptions.setNumThreads(2);
            cpuOptions.setUseXNNPACK(false);
            tfliteInterpreter = new Interpreter(buffer, cpuOptions);
            isModelLoaded = true;
            modelInitError = null;
            Log.i(TAG, "TFLite model [" + MODEL_VERSION + "] initialized successfully with standard CPU.");
            return;
        } catch (Throwable t2) {
            Log.w(TAG, "Interpreter init with CPU options failed: " + t2.getMessage() + ". Retrying bare interpreter...", t2);
            lastError = t2;
        }

        // Tier 3: Bare default Interpreter
        try {
            buffer.rewind();
            tfliteInterpreter = new Interpreter(buffer);
            isModelLoaded = true;
            modelInitError = null;
            Log.i(TAG, "TFLite model [" + MODEL_VERSION + "] initialized with bare default options.");
            return;
        } catch (Throwable t3) {
            Log.e(TAG, "All Interpreter initialization attempts failed: " + t3.getMessage(), t3);
            lastError = t3;
        }

        isModelLoaded = false;
        tfliteInterpreter = null;
        modelInitError = lastError != null ? lastError.getClass().getSimpleName() + ": " + lastError.getMessage() : "Unknown init error";
    }

    /**
     * Robust multi-strategy model loader:
     * 1. Direct InputStream -> Direct ByteBuffer (immune to APK compression & OS file descriptor closure)
     * 2. AssetFileDescriptor -> FileChannel.map (keeping file descriptor open)
     * 3. App-private cache directory fallback
     */
    private ByteBuffer loadModelBuffer(String modelPath) throws IOException {
        // Strategy 1: Direct InputStream -> Direct ByteBuffer
        // This is 100% resilient across all Android versions, ROMs (ColorOS, MIUI, OneUI),
        // and works whether the asset in the APK is compressed or uncompressed.
        try (InputStream is = context.getAssets().open(modelPath)) {
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            byte[] chunk = new byte[32768];
            int read;
            while ((read = is.read(chunk)) != -1) {
                baos.write(chunk, 0, read);
            }
            byte[] modelBytes = baos.toByteArray();
            if (modelBytes.length > 0) {
                Log.i(TAG, "Successfully read " + modelBytes.length + " bytes for " + modelPath + " via direct asset stream.");
                ByteBuffer directBuffer = ByteBuffer.allocateDirect(modelBytes.length);
                directBuffer.order(ByteOrder.nativeOrder());
                directBuffer.put(modelBytes);
                directBuffer.rewind();
                return directBuffer;
            }
        } catch (Throwable t1) {
            Log.w(TAG, "Direct asset stream reading failed (" + t1.getMessage() + "). Trying AssetFileDescriptor...", t1);
        }

        // Strategy 2: AssetFileDescriptor memory mapping (retaining descriptor references)
        try {
            activeModelAfd = context.getAssets().openFd(modelPath);
            activeFis = new FileInputStream(activeModelAfd.getFileDescriptor());
            FileChannel fileChannel = activeFis.getChannel();
            long startOffset = activeModelAfd.getStartOffset();
            long declaredLength = activeModelAfd.getDeclaredLength();
            MappedByteBuffer mappedBuffer = fileChannel.map(FileChannel.MapMode.READ_ONLY, startOffset, declaredLength);
            Log.i(TAG, "Successfully mapped " + declaredLength + " bytes for " + modelPath + " via AssetFileDescriptor.");
            return mappedBuffer;
        } catch (Throwable t2) {
            Log.w(TAG, "AssetFileDescriptor mapping failed (" + t2.getMessage() + "). Trying cache file copy...", t2);
        }

        // Strategy 3: Copy to app's private cache directory
        File cacheFile = new File(context.getCacheDir(), modelPath);
        if (!cacheFile.exists() || cacheFile.length() == 0) {
            try (InputStream in = context.getAssets().open(modelPath);
                 FileOutputStream out = new FileOutputStream(cacheFile)) {
                byte[] buf = new byte[32768];
                int len;
                while ((len = in.read(buf)) > 0) {
                    out.write(buf, 0, len);
                }
            }
        }
        FileInputStream fis = new FileInputStream(cacheFile);
        FileChannel fc = fis.getChannel();
        return fc.map(FileChannel.MapMode.READ_ONLY, 0, cacheFile.length());
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
            Log.w(TAG, "Classifier invoked while model is not loaded. Detail: " + modelInitError);
            String message = modelInitError != null
                    ? "AI model initialization issue (" + modelInitError + "). Please select manually."
                    : "AI model unavailable. Please select the category manually.";
            return PredictionResult.createFallback(
                    message,
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
                    isLowConfidence ? "Low confidence. Please verify category." : ""
            );
        } catch (Exception e) {
            Log.e(TAG, "TFLite inference runtime failure: " + e.getMessage(), e);
            return PredictionResult.createFallback(
                    "Inference error (" + e.getMessage() + "). Please select manually.",
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
        if (activeFis != null) {
            try {
                activeFis.close();
            } catch (Exception ignored) {}
            activeFis = null;
        }
        if (activeModelAfd != null) {
            try {
                activeModelAfd.close();
            } catch (Exception ignored) {}
            activeModelAfd = null;
        }
        isModelLoaded = false;
        executorService.shutdown();
    }
}
