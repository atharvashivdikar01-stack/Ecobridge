package com.ecobridge.ai.deepscan;

import java.util.Locale;

/**
 * DefaultSafetyAnalyzer
 * Implements rule-based safety and PPE directives based on detected scrap categories.
 */
public class DefaultSafetyAnalyzer implements SafetyAnalyzer {

    @Override
    public HazardAssessment assessSafety(String category, float confidence) {
        if (category == null) {
            return new HazardAssessment(false, "", "Standard handling gloves");
        }

        String lower = category.toLowerCase(Locale.US);

        if (lower.contains("batter") || lower.contains("mobile") || lower.contains("phone") || lower.contains("cell") || lower.contains("smartphone")) {
            return new HazardAssessment(
                    true,
                    "Internal Battery Hazard! Mobile electronic devices contain lithium-ion/polymer cells prone to thermal runaway, swelling, and chemical fire. Do not puncture or crush.",
                    "Fire-resistant gloves, protective eyewear"
            );
        } else if (lower.contains("crt")) {
            return new HazardAssessment(
                    true,
                    "Hazardous CRT glass! High vacuum implosion risk and toxic leaded glass funnel. Handle with care; do not crack screen.",
                    "Heavy-duty cut-resistant gloves, full face shield"
            );
        } else if (lower.contains("pcb") || lower.contains("circuit board")) {
            return new HazardAssessment(
                    false, // Notice: not emergency critical hazard, but contains lead solder notice
                    "Contains lead solder and capacitor charges. Avoid skin contact and inhalation of dust.",
                    "General work gloves, dust mask"
            );
        } else if (lower.contains("cable") || lower.contains("wire")) {
            return new HazardAssessment(
                    false,
                    "Never burn cables to strip insulation. Open burning releases carcinogenic dioxins.",
                    "Mechanical wire stripping tool, cut-resistant gloves"
            );
        }

        return new HazardAssessment(false, "", "Standard handling gloves");
    }
}
