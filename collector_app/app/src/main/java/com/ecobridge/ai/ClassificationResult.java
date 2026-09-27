package com.ecobridge.ai;

/**
 * ClassificationResult
 * Holds model inference outcome, category prediction, confidence score,
 * and automated hazard evaluation flags.
 */
public class ClassificationResult {

    private final String category;
    private final float confidence;
    private final boolean isHazardous;
    private final String hazardWarning;

    public ClassificationResult(String category, float confidence, boolean isHazardous, String hazardWarning) {
        this.category = category;
        this.confidence = confidence;
        this.isHazardous = isHazardous;
        this.hazardWarning = hazardWarning;
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
}
