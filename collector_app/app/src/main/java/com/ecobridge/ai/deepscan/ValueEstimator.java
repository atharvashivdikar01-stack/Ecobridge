package com.ecobridge.ai.deepscan;

/**
 * ValueEstimator
 * Looks up verified market benchmarks for recognized components and materials.
 * Explicitly avoids fabricating prices directly from raw images; instead grounds
 * estimates in authoritative market registry data.
 */
public interface ValueEstimator {

    class ValueRange {
        private final double minPricePerKg;
        private final double maxPricePerKg;
        private final double benchmarkPricePerKg;
        private final String priceSource;

        public ValueRange(double minPricePerKg, double maxPricePerKg, double benchmarkPricePerKg, String priceSource) {
            this.minPricePerKg = minPricePerKg;
            this.maxPricePerKg = maxPricePerKg;
            this.benchmarkPricePerKg = benchmarkPricePerKg;
            this.priceSource = priceSource;
        }

        public double getMinPricePerKg() {
            return minPricePerKg;
        }

        public double getMaxPricePerKg() {
            return maxPricePerKg;
        }

        public double getBenchmarkPricePerKg() {
            return benchmarkPricePerKg;
        }

        public String getPriceSource() {
            return priceSource;
        }
    }

    ValueRange estimateValueRange(String category);
}
