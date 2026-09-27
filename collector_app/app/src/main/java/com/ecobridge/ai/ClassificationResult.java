package com.ecobridge.ai;

import java.util.Collections;
import java.util.List;

/**
 * ClassificationResult
 * Holds model inference outcome, category prediction, confidence score,
 * automated hazard evaluation flags, and detailed PredictionResult metadata.
 */
public class ClassificationResult {

    private final String category;
    private final float confidence;
    private final boolean isHazardous;
    private final String hazardWarning;
    private final PredictionResult predictionResult;

    public ClassificationResult(String category, float confidence, boolean isHazardous, String hazardWarning) {
        this(category, confidence, isHazardous, hazardWarning, null);
    }

    public ClassificationResult(String category,
                                float confidence,
                                boolean isHazardous,
                                String hazardWarning,
                                PredictionResult predictionResult) {
        this.category = category;
        this.confidence = confidence;
        this.isHazardous = isHazardous;
        this.hazardWarning = hazardWarning;
        this.predictionResult = predictionResult;
    }

    public static ClassificationResult fromPredictionResult(PredictionResult pr) {
        return new ClassificationResult(
                pr.getCategory(),
                pr.getConfidence(),
                pr.isHazardous(),
                pr.getHazardWarning(),
                pr
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

    public boolean isHazardous() {
        return isHazardous;
    }

    public String getHazardWarning() {
        return hazardWarning;
    }

    public PredictionResult getPredictionResult() {
        return predictionResult;
    }

    public List<CategoryPrediction> getTopPredictions() {
        if (predictionResult != null) {
            return predictionResult.getTopPredictions();
        }
        return Collections.emptyList();
    }

    public String getModelVersion() {
        return predictionResult != null ? predictionResult.getModelVersion() : "mobilenet_scrap_v1";
    }

    public long getInferenceTimeMs() {
        return predictionResult != null ? predictionResult.getInferenceTimeMs() : 0L;
    }

    public boolean isLowConfidence() {
        return predictionResult != null && predictionResult.isLowConfidence();
    }
}
