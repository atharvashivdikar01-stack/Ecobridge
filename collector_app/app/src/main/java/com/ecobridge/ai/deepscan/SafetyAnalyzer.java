package com.ecobridge.ai.deepscan;

/**
 * SafetyAnalyzer
 * Contract and analyzer for detecting hazardous conditions (batteries, CRT glass, burnt PCBs)
 * and providing worker safety / PPE alerts prior to valuation.
 */
public interface SafetyAnalyzer {

    class HazardAssessment {
        private final boolean hazardous;
        private final String hazardWarning;
        private final String requiredPpe;

        public HazardAssessment(boolean hazardous, String hazardWarning, String requiredPpe) {
            this.hazardous = hazardous;
            this.hazardWarning = hazardWarning != null ? hazardWarning : "";
            this.requiredPpe = requiredPpe != null ? requiredPpe : "";
        }

        public boolean isHazardous() {
            return hazardous;
        }

        public String getHazardWarning() {
            return hazardWarning;
        }

        public String getRequiredPpe() {
            return requiredPpe;
        }
    }

    HazardAssessment assessSafety(String category, float confidence);
}
