package com.ecobridge.data.local.entity;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.Ignore;
import androidx.room.Index;
import androidx.room.PrimaryKey;

/**
 * LotEntity
 * Represents a registered scrap batch created on the mobile device.
 * Serves as the primary source of truth for offline collections,
 * tracking material categorization, AI inference results, and collector confirmations.
 */
@Entity(tableName = "lots", indices = {@Index("shortCode"), @Index("syncStatus")})
public class LotEntity {

    @PrimaryKey
    @NonNull
    private String uuid;

    private String shortCode; // e.g. "LOT-7F29A"
    private String category;  // e.g. "Copper Cables & Wires", "Printed Circuit Boards (PCBs)"
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

    // AI Recognition & Data Flywheel fields
    private String aiCategory;                 // Original AI classification (e.g. "Printed Circuit Boards (PCBs)")
    private double aiConfidence;               // Model confidence score (e.g. 0.94)
    private String collectorConfirmedCategory; // Collector confirmed or corrected material
    private String aiModelVersion;             // Model identifier (e.g. "mobilenet_scrap_v1")
    private String imageHash;                  // SHA-256 integrity hash of captured photograph

    @Ignore
    public LotEntity(@NonNull String uuid, String shortCode, String category,
                     double approxWeightKg, double quotedPrice, double estimatedValue,
                     double netEarnings, String selectedRecyclerId, String selectedRecyclerName,
                     String status, String createdAt, String updatedAt, String syncStatus) {
        this(uuid, shortCode, category, approxWeightKg, quotedPrice, estimatedValue,
                netEarnings, selectedRecyclerId, selectedRecyclerName, status, createdAt, updatedAt, syncStatus,
                category, 1.0, category, "mobilenet_scrap_v1", "");
    }

    public LotEntity(@NonNull String uuid, String shortCode, String category,
                     double approxWeightKg, double quotedPrice, double estimatedValue,
                     double netEarnings, String selectedRecyclerId, String selectedRecyclerName,
                     String status, String createdAt, String updatedAt, String syncStatus,
                     String aiCategory, double aiConfidence, String collectorConfirmedCategory,
                     String aiModelVersion, String imageHash) {
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
        this.aiCategory = aiCategory != null ? aiCategory : "";
        this.aiConfidence = aiConfidence;
        this.collectorConfirmedCategory = collectorConfirmedCategory != null ? collectorConfirmedCategory : category;
        this.aiModelVersion = aiModelVersion != null ? aiModelVersion : "mobilenet_scrap_v1";
        this.imageHash = imageHash != null ? imageHash : "";
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

    public String getAiCategory() {
        return aiCategory;
    }

    public void setAiCategory(String aiCategory) {
        this.aiCategory = aiCategory;
    }

    public double getAiConfidence() {
        return aiConfidence;
    }

    public void setAiConfidence(double aiConfidence) {
        this.aiConfidence = aiConfidence;
    }

    public String getCollectorConfirmedCategory() {
        return collectorConfirmedCategory;
    }

    public void setCollectorConfirmedCategory(String collectorConfirmedCategory) {
        this.collectorConfirmedCategory = collectorConfirmedCategory;
    }

    public String getAiModelVersion() {
        return aiModelVersion;
    }

    public void setAiModelVersion(String aiModelVersion) {
        this.aiModelVersion = aiModelVersion;
    }

    public String getImageHash() {
        return imageHash;
    }

    public void setImageHash(String imageHash) {
        this.imageHash = imageHash;
    }
}
