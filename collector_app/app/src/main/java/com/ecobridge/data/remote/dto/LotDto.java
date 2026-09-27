package com.ecobridge.data.remote.dto;

import com.google.gson.annotations.SerializedName;

public class LotDto {

    @SerializedName("uuid")
    private String uuid;

    @SerializedName("short_code")
    private String shortCode;

    @SerializedName("category")
    private String category;

    @SerializedName("approx_weight_kg")
    private double approxWeightKg;

    @SerializedName("quoted_price")
    private double quotedPrice;

    @SerializedName("net_earnings")
    private double netEarnings;

    @SerializedName("selected_recycler_id")
    private String selectedRecyclerId;

    @SerializedName("status")
    private String status;

    @SerializedName("created_at")
    private String createdAt;

    @SerializedName("ai_category")
    private String aiCategory;

    @SerializedName("ai_confidence")
    private double aiConfidence;

    @SerializedName("collector_confirmed_category")
    private String collectorConfirmedCategory;

    @SerializedName("ai_model_version")
    private String aiModelVersion;

    @SerializedName("image_hash")
    private String imageHash;

    public LotDto() {}

    public LotDto(String uuid, String shortCode, String category, double approxWeightKg,
                  double quotedPrice, double netEarnings, String selectedRecyclerId,
                  String status, String createdAt) {
        this(uuid, shortCode, category, approxWeightKg, quotedPrice, netEarnings, selectedRecyclerId,
                status, createdAt, category, 1.0, category, "mobilenet_scrap_v1", "");
    }

    public LotDto(String uuid, String shortCode, String category, double approxWeightKg,
                  double quotedPrice, double netEarnings, String selectedRecyclerId,
                  String status, String createdAt, String aiCategory, double aiConfidence,
                  String collectorConfirmedCategory, String aiModelVersion, String imageHash) {
        this.uuid = uuid;
        this.shortCode = shortCode;
        this.category = category;
        this.approxWeightKg = approxWeightKg;
        this.quotedPrice = quotedPrice;
        this.netEarnings = netEarnings;
        this.selectedRecyclerId = selectedRecyclerId;
        this.status = status;
        this.createdAt = createdAt;
        this.aiCategory = aiCategory;
        this.aiConfidence = aiConfidence;
        this.collectorConfirmedCategory = collectorConfirmedCategory;
        this.aiModelVersion = aiModelVersion;
        this.imageHash = imageHash;
    }

    public String getUuid() { return uuid; }
    public void setUuid(String uuid) { this.uuid = uuid; }

    public String getShortCode() { return shortCode; }
    public void setShortCode(String shortCode) { this.shortCode = shortCode; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public double getApproxWeightKg() { return approxWeightKg; }
    public void setApproxWeightKg(double approxWeightKg) { this.approxWeightKg = approxWeightKg; }

    public double getQuotedPrice() { return quotedPrice; }
    public void setQuotedPrice(double quotedPrice) { this.quotedPrice = quotedPrice; }

    public double getNetEarnings() { return netEarnings; }
    public void setNetEarnings(double netEarnings) { this.netEarnings = netEarnings; }

    public String getSelectedRecyclerId() { return selectedRecyclerId; }
    public void setSelectedRecyclerId(String selectedRecyclerId) { this.selectedRecyclerId = selectedRecyclerId; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }

    public String getAiCategory() { return aiCategory; }
    public void setAiCategory(String aiCategory) { this.aiCategory = aiCategory; }

    public double getAiConfidence() { return aiConfidence; }
    public void setAiConfidence(double aiConfidence) { this.aiConfidence = aiConfidence; }

    public String getCollectorConfirmedCategory() { return collectorConfirmedCategory; }
    public void setCollectorConfirmedCategory(String collectorConfirmedCategory) { this.collectorConfirmedCategory = collectorConfirmedCategory; }

    public String getAiModelVersion() { return aiModelVersion; }
    public void setAiModelVersion(String aiModelVersion) { this.aiModelVersion = aiModelVersion; }

    public String getImageHash() { return imageHash; }
    public void setImageHash(String imageHash) { this.imageHash = imageHash; }
}
