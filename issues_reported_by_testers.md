# Issues Reported by Testers & Status Tracker

| Issue # | Description | Root Cause | Status & Remediation |
|---|---|---|---|
| **1** | AI is not able to detect items reliably in certain lighting conditions | MobileNetV2 requires CLAHE / normalized lighting; fine-grained physical condition detection is unproven on-device | ✅ **RESOLVED (HONEST UX)**: Relabeled AI classification as "Category Assistance". Implemented dual-mode feature analyzer fallback with 1-tap manual category correction grid. |
| **2** | AI needs more training on mixed materials | Training dataset lacks cluttered multi-class scrap yard piles | 📋 **DOCUMENTED FOR ROADMAP**: Future YOLOv8-Nano segmentation model planned on real scrap dataset. In MVP, user confirms primary dominant material category. |
| **3** | We tried wire, it was showing PCB | Reddish/copper wire traces shared high chromatic similarity with copper PCB tracks | ✅ **RESOLVED**: Recalibrated wire vs PCB feature weights in fallback analyzer. Added dedicated wire stripping hazard guideline in `DefaultSafetyAnalyzer`. |
| **4** | We tried mobile, it was showing mix of plastic, and mobile contains battery, but no hazard warning was shown | `DefaultSafetyAnalyzer` only checked for the explicit substring `"batter"` in category name | ✅ **RESOLVED**: Updated `DefaultSafetyAnalyzer.java` to trigger mandatory critical battery hazard warning and PPE requirements for any mobile/phone/cell/smartphone device, protecting informal pickers from lithium thermal runaway. |
