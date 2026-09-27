package com.ecobridge.ai.deepscan;

import android.graphics.Bitmap;
import android.graphics.RectF;

import java.util.List;

/**
 * ComponentDetector
 * Interface for future DeepScan component detection (e.g. capacitors, ICs, copper coils, transformers).
 */
public interface ComponentDetector {

    class DetectedComponent {
        private final String componentName;
        private final float confidence;
        private final RectF boundingBox;

        public DetectedComponent(String componentName, float confidence, RectF boundingBox) {
            this.componentName = componentName;
            this.confidence = confidence;
            this.boundingBox = boundingBox;
        }

        public String getComponentName() {
            return componentName;
        }

        public float getConfidence() {
            return confidence;
        }

        public RectF getBoundingBox() {
            return boundingBox;
        }
    }

    List<DetectedComponent> detectComponents(Bitmap image);
}
