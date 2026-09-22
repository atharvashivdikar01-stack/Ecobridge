package com.ecobridge.data.remote.dto;

import com.google.gson.annotations.SerializedName;

public class HandoverDto {

    @SerializedName("uuid")
    private String uuid;

    @SerializedName("reference_no")
    private String referenceNo;

    @SerializedName("lot_id")
    private String lotId;

    @SerializedName("recycler_id")
    private String recyclerId;

    @SerializedName("weight")
    private double weight;

    @SerializedName("agreed_price")
    private double agreedPrice;

    @SerializedName("record_hash")
    private String recordHash;

    @SerializedName("payment_mode")
    private String paymentMode;

    @SerializedName("payment_amount")
    private double paymentAmount;

    @SerializedName("payment_status")
    private String paymentStatus;

    @SerializedName("created_at")
    private String createdAt;

    public HandoverDto() {}

    public HandoverDto(String uuid, String referenceNo, String lotId, String recyclerId,
                       double weight, double agreedPrice, String recordHash, String paymentMode,
                       double paymentAmount, String paymentStatus, String createdAt) {
        this.uuid = uuid;
        this.referenceNo = referenceNo;
        this.lotId = lotId;
        this.recyclerId = recyclerId;
        this.weight = weight;
        this.agreedPrice = agreedPrice;
        this.recordHash = recordHash;
        this.paymentMode = paymentMode;
        this.paymentAmount = paymentAmount;
        this.paymentStatus = paymentStatus;
        this.createdAt = createdAt;
    }

    public String getUuid() { return uuid; }
    public void setUuid(String uuid) { this.uuid = uuid; }

    public String getReferenceNo() { return referenceNo; }
    public void setReferenceNo(String referenceNo) { this.referenceNo = referenceNo; }

    public String getLotId() { return lotId; }
    public void setLotId(String lotId) { this.lotId = lotId; }

    public String getRecyclerId() { return recyclerId; }
    public void setRecyclerId(String recyclerId) { this.recyclerId = recyclerId; }

    public double getWeight() { return weight; }
    public void setWeight(double weight) { this.weight = weight; }

    public double getAgreedPrice() { return agreedPrice; }
    public void setAgreedPrice(double agreedPrice) { this.agreedPrice = agreedPrice; }

    public String getRecordHash() { return recordHash; }
    public void setRecordHash(String recordHash) { this.recordHash = recordHash; }

    public String getPaymentMode() { return paymentMode; }
    public void setPaymentMode(String paymentMode) { this.paymentMode = paymentMode; }

    public double getPaymentAmount() { return paymentAmount; }
    public void setPaymentAmount(double paymentAmount) { this.paymentAmount = paymentAmount; }

    public String getPaymentStatus() { return paymentStatus; }
    public void setPaymentStatus(String paymentStatus) { this.paymentStatus = paymentStatus; }

    public String getCreatedAt() { return createdAt; }
    public void setCreatedAt(String createdAt) { this.createdAt = createdAt; }
}
