package com.ecobridge.ai;

/**
 * CategoryPrediction
 * Represents an individual class prediction with confidence score and rank.
 */
public class CategoryPrediction {

    private final String category;
    private final float confidence;
    private final int rank;

    public CategoryPrediction(String category, float confidence, int rank) {
        this.category = category;
        this.confidence = confidence;
        this.rank = rank;
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

    public int getRank() {
        return rank;
    }

    @Override
    public String toString() {
        return rank + ". " + category + " (" + getConfidencePercentage() + "%)";
    }
}
