package com.ecobridge.ai;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/**
 * PredictionResult
 * Comprehensive AI inference result holding the primary prediction,
 * confidence score, top-N predictions, inference runtime, hazard evaluation,
 * and model version identifier.
 */
public class PredictionResult {

    public enum Status {
        SUCCESS,
        LOW_CONFIDENCE,
        MODEL_UNAVAILABLE,
        INVALID_IMAGE,
        ERROR
    }

    private final String category;
    private final float confidence;
    private final List<CategoryPrediction> topPredictions;
    private final boolean isHazardous;
    private final String hazardWarning;
    private final boolean isLowConfidence;
    private final String modelVersion;
    private final long inferenceTimeMs;
    private final Status status;
    private final String errorMessage;

    public PredictionResult(String category,
                            float confidence,
                            List<CategoryPrediction> topPredictions,
                            boolean isHazardous,
                            String hazardWarning,
                            boolean isLowConfidence,
                            String modelVersion,
                            long inferenceTimeMs,
                            Status status,
                            String errorMessage) {
        this.category = category != null ? category : "";
        this.confidence = confidence;
        this.topPredictions = topPredictions != null ? topPredictions : new ArrayList<>();
        this.isHazardous = isHazardous;
        this.hazardWarning = hazardWarning != null ? hazardWarning : "";
        this.isLowConfidence = isLowConfidence;
        this.modelVersion = modelVersion != null ? modelVersion : "mobilenet_scrap_v1";
        this.inferenceTimeMs = inferenceTimeMs;
        this.status = status;
        this.errorMessage = errorMessage != null ? errorMessage : "";
    }

    public static PredictionResult createFallback(String message, Status status) {
        return new PredictionResult(
                "Other Electronic Scrap",
                0.0f,
                Collections.emptyList(),
                false,
                "",
                true,
                "none",
                0L,
                status,
                message
        );
    }

    public String getCategory() {
        return category;
    }

    public float getConfidence() {
        return confidence;
    }

    public int getConfidencePercentage() {
        return Math.round(confidence * 100);
    }

    public List<CategoryPrediction> getTopPredictions() {
        return Collections.unmodifiableList(topPredictions);
    }

    public boolean isHazardous() {
        return isHazardous;
    }

    public String getHazardWarning() {
        return hazardWarning;
    }

    public boolean isLowConfidence() {
        return isLowConfidence;
    }

    public String getModelVersion() {
        return modelVersion;
    }

    public long getInferenceTimeMs() {
        return inferenceTimeMs;
    }

    public Status getStatus() {
        return status;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public boolean isSuccess() {
        return status == Status.SUCCESS || status == Status.LOW_CONFIDENCE;
    }
}
