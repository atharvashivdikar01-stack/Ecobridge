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

    public LotDto() {}

    public LotDto(String uuid, String shortCode, String category, double approxWeightKg,
                  double quotedPrice, double netEarnings, String selectedRecyclerId,
                  String status, String createdAt) {
        this.uuid = uuid;
        this.shortCode = shortCode;
        this.category = category;
        this.approxWeightKg = approxWeightKg;
        this.quotedPrice = quotedPrice;
        this.netEarnings = netEarnings;
        this.selectedRecyclerId = selectedRecyclerId;
        this.status = status;
        this.createdAt = createdAt;
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
}
