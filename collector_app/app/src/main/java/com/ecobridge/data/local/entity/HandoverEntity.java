package com.ecobridge.data.local.entity;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.ForeignKey;
import androidx.room.Index;
import androidx.room.PrimaryKey;

/**
 * HandoverEntity
 * Represents the verified transfer of scrap lot custody to a recycler,
 * including final weight confirmation, cash/digital payment receipt,
 * and deterministic tamper-evident audit record hash.
 */
@Entity(tableName = "handovers",
        foreignKeys = @ForeignKey(entity = LotEntity.class,
                parentColumns = "uuid",
                childColumns = "lotId",
                onDelete = ForeignKey.CASCADE),
        indices = {@Index("lotId"), @Index("referenceNo"), @Index("syncStatus")})
public class HandoverEntity {

    @PrimaryKey
    @NonNull
    private String uuid;

    private String referenceNo; // e.g. "HO-8B391A"
    private String lotId;
    private String recyclerId;
    private String recyclerName;
    private double weight;
    private double agreedPrice;
    private String recordHash; // Deterministic SHA-256
    private String paymentMode; // CASH, DIGITAL
    private double paymentAmount;
    private String paymentStatus; // PAID, PENDING
    private String createdAt;
    private String syncStatus; // PENDING, SYNCING, SYNCED, FAILED

    public HandoverEntity(@NonNull String uuid, String referenceNo, String lotId,
                          String recyclerId, String recyclerName, double weight, double agreedPrice,
                          String recordHash, String paymentMode, double paymentAmount,
                          String paymentStatus, String createdAt, String syncStatus) {
        this.uuid = uuid;
        this.referenceNo = referenceNo;
        this.lotId = lotId;
        this.recyclerId = recyclerId;
        this.recyclerName = recyclerName;
        this.weight = weight;
        this.agreedPrice = agreedPrice;
        this.recordHash = recordHash;
        this.paymentMode = paymentMode;
        this.paymentAmount = paymentAmount;
        this.paymentStatus = paymentStatus;
        this.createdAt = createdAt;
        this.syncStatus = syncStatus;
    }

    @NonNull
    public String getUuid() {
        return uuid;
    }

    public void setUuid(@NonNull String uuid) {
        this.uuid = uuid;
    }

    public String getReferenceNo() {
        return referenceNo;
    }

    public void setReferenceNo(String referenceNo) {
        this.referenceNo = referenceNo;
    }

    public String getLotId() {
        return lotId;
    }

    public void setLotId(String lotId) {
        this.lotId = lotId;
    }

    public String getRecyclerId() {
        return recyclerId;
    }

    public void setRecyclerId(String recyclerId) {
        this.recyclerId = recyclerId;
    }

    public String getRecyclerName() {
        return recyclerName;
    }

    public void setRecyclerName(String recyclerName) {
        this.recyclerName = recyclerName;
    }

    public double getWeight() {
        return weight;
    }

    public void setWeight(double weight) {
        this.weight = weight;
    }

    public double getAgreedPrice() {
        return agreedPrice;
    }

    public void setAgreedPrice(double agreedPrice) {
        this.agreedPrice = agreedPrice;
    }

    public String getRecordHash() {
        return recordHash;
    }

    public void setRecordHash(String recordHash) {
        this.recordHash = recordHash;
    }

    public String getPaymentMode() {
        return paymentMode;
    }

    public void setPaymentMode(String paymentMode) {
        this.paymentMode = paymentMode;
    }

    public double getPaymentAmount() {
        return paymentAmount;
    }

    public void setPaymentAmount(double paymentAmount) {
        this.paymentAmount = paymentAmount;
    }

    public String getPaymentStatus() {
        return paymentStatus;
    }

    public void setPaymentStatus(String paymentStatus) {
        this.paymentStatus = paymentStatus;
    }

    public String getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(String createdAt) {
        this.createdAt = createdAt;
    }

    public String getSyncStatus() {
        return syncStatus;
    }

    public void setSyncStatus(String syncStatus) {
        this.syncStatus = syncStatus;
    }
}
