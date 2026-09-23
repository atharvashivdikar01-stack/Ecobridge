package com.ecobridge.data.local.entity;

import androidx.room.Entity;
import androidx.room.Index;
import androidx.room.PrimaryKey;

/**
 * PriceEntity
 * Caches benchmark scrap commodity rates locally on the collector's device
 * ensuring transparent pricing even in remote zero-network conditions.
 */
@Entity(tableName = "prices", indices = {@Index(value = {"category"}, unique = true)})
public class PriceEntity {

    @PrimaryKey(autoGenerate = true)
    private int id;

    private String category;
    private double buyingPrice;
    private double sellingPrice;
    private String sourceType; // "DEMO_DATASET", "FIELD_OBSERVATION", "CERTIFIED_RECYCLER"
    private String observedAt;
    private String updatedAt;

    public PriceEntity(String category, double buyingPrice, double sellingPrice,
                       String sourceType, String observedAt, String updatedAt) {
        this.category = category;
        this.buyingPrice = buyingPrice;
        this.sellingPrice = sellingPrice;
        this.sourceType = sourceType;
        this.observedAt = observedAt;
        this.updatedAt = updatedAt;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public double getBuyingPrice() {
        return buyingPrice;
    }

    public void setBuyingPrice(double buyingPrice) {
        this.buyingPrice = buyingPrice;
    }

    public double getSellingPrice() {
        return sellingPrice;
    }

    public void setSellingPrice(double sellingPrice) {
        this.sellingPrice = sellingPrice;
    }

    public String getSourceType() {
        return sourceType;
    }

    public void setSourceType(String sourceType) {
        this.sourceType = sourceType;
    }

    public String getObservedAt() {
        return observedAt;
    }

    public void setObservedAt(String observedAt) {
        this.observedAt = observedAt;
    }

    public String getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(String updatedAt) {
        this.updatedAt = updatedAt;
    }
}
