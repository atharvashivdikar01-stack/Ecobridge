package com.ecobridge.data.local.entity;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.Index;
import androidx.room.PrimaryKey;

/**
 * LotEntity
 * Represents a registered scrap batch created on the mobile device.
 * Serves as the primary source of truth for offline collections.
 */
@Entity(tableName = "lots", indices = {@Index("shortCode"), @Index("syncStatus")})
public class LotEntity {

    @PrimaryKey
    @NonNull
    private String uuid;

    private String shortCode; // e.g. "LOT-7F29A"
    private String category;  // e.g. "Copper", "Aluminium", "PCB"
    private double approxWeightKg;
    private double quotedPrice; // Unit price per kg (e.g. ₹420.00)
    private double estimatedValue; // approxWeightKg * quotedPrice
    private double netEarnings; // EstimatedValue - Transport - Handling
    private String selectedRecyclerId;
    private String selectedRecyclerName;
    private String status; // CREATED, MATCHED, OFFER_ACCEPTED, READY_FOR_HANDOVER, HANDOVER_CONFIRMED, PAYMENT_CONFIRMED, RECEIVED
    private String createdAt;
    private String updatedAt;
    private String syncStatus; // PENDING, SYNCING, SYNCED, FAILED

    public LotEntity(@NonNull String uuid, String shortCode, String category,
                     double approxWeightKg, double quotedPrice, double estimatedValue,
                     double netEarnings, String selectedRecyclerId, String selectedRecyclerName,
                     String status, String createdAt, String updatedAt, String syncStatus) {
        this.uuid = uuid;
        this.shortCode = shortCode;
        this.category = category;
        this.approxWeightKg = approxWeightKg;
        this.quotedPrice = quotedPrice;
        this.estimatedValue = estimatedValue;
        this.netEarnings = netEarnings;
        this.selectedRecyclerId = selectedRecyclerId;
        this.selectedRecyclerName = selectedRecyclerName;
        this.status = status;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
        this.syncStatus = syncStatus;
    }

    @NonNull
    public String getUuid() {
        return uuid;
    }

    public void setUuid(@NonNull String uuid) {
        this.uuid = uuid;
    }

    public String getShortCode() {
        return shortCode;
    }

    public void setShortCode(String shortCode) {
        this.shortCode = shortCode;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public double getApproxWeightKg() {
        return approxWeightKg;
    }

    public void setApproxWeightKg(double approxWeightKg) {
        this.approxWeightKg = approxWeightKg;
    }

    public double getQuotedPrice() {
        return quotedPrice;
    }

    public void setQuotedPrice(double quotedPrice) {
        this.quotedPrice = quotedPrice;
    }

    public double getEstimatedValue() {
        return estimatedValue;
    }

    public void setEstimatedValue(double estimatedValue) {
        this.estimatedValue = estimatedValue;
    }

    public double getNetEarnings() {
        return netEarnings;
    }

    public void setNetEarnings(double netEarnings) {
        this.netEarnings = netEarnings;
    }

    public String getSelectedRecyclerId() {
        return selectedRecyclerId;
    }

    public void setSelectedRecyclerId(String selectedRecyclerId) {
        this.selectedRecyclerId = selectedRecyclerId;
    }

    public String getSelectedRecyclerName() {
        return selectedRecyclerName;
    }

    public void setSelectedRecyclerName(String selectedRecyclerName) {
        this.selectedRecyclerName = selectedRecyclerName;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(String createdAt) {
        this.createdAt = createdAt;
    }

    public String getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(String updatedAt) {
        this.updatedAt = updatedAt;
    }

    public String getSyncStatus() {
        return syncStatus;
    }

    public void setSyncStatus(String syncStatus) {
        this.syncStatus = syncStatus;
    }
}
