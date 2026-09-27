package com.ecobridge.ai.deepscan;

import android.graphics.Bitmap;

import java.util.List;

/**
 * OcrAnalyzer
 * Interface for reading serial numbers, chip part numbers, and manufacturer codes from scrap.
 */
public interface OcrAnalyzer {

    class TextBlock {
        private final String text;
        private final float confidence;

        public TextBlock(String text, float confidence) {
            this.text = text;
            this.confidence = confidence;
        }

        public String getText() {
            return text;
        }

        public float getConfidence() {
            return confidence;
        }
    }

    List<TextBlock> extractText(Bitmap image);
}
