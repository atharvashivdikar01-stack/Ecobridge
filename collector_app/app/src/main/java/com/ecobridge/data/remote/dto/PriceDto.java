package com.ecobridge.data.remote.dto;

import com.google.gson.annotations.SerializedName;

public class PriceDto {

    @SerializedName("id")
    private int id;

    @SerializedName("category")
    private String category;

    @SerializedName("buying_price")
    private double buyingPrice;

    @SerializedName("selling_price")
    private double sellingPrice;

    @SerializedName("source_type")
    private String sourceType;

    @SerializedName("observed_at")
    private String observedAt;

    public int getId() { return id; }
    public void setId(int id) { this.id = id; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public double getBuyingPrice() { return buyingPrice; }
    public void setBuyingPrice(double buyingPrice) { this.buyingPrice = buyingPrice; }

    public double getSellingPrice() { return sellingPrice; }
    public void setSellingPrice(double sellingPrice) { this.sellingPrice = sellingPrice; }

    public String getSourceType() { return sourceType; }
    public void setSourceType(String sourceType) { this.sourceType = sourceType; }

    public String getObservedAt() { return observedAt; }
    public void setObservedAt(String observedAt) { this.observedAt = observedAt; }
}
