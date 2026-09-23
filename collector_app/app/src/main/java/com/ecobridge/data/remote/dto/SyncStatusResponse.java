package com.ecobridge.data.remote.dto;

import com.google.gson.annotations.SerializedName;

import java.util.List;

/** Server-confirmed transitions for records already persisted in Room. */
public class SyncStatusResponse {
    @SerializedName("lots") private List<LotStatus> lots;
    @SerializedName("handovers") private List<HandoverStatus> handovers;

    public List<LotStatus> getLots() { return lots; }
    public List<HandoverStatus> getHandovers() { return handovers; }

    public static class LotStatus {
        @SerializedName("lot_code") private String lotCode;
        private String status;
        public String getLotCode() { return lotCode; }
        public String getStatus() { return status; }
    }

    public static class HandoverStatus {
        @SerializedName("reference_no") private String referenceNo;
        private String status;
        @SerializedName("payment_status") private String paymentStatus;
        @SerializedName("payment_amount") private Double paymentAmount;
        public String getReferenceNo() { return referenceNo; }
        public String getStatus() { return status; }
        public String getPaymentStatus() { return paymentStatus; }
        public Double getPaymentAmount() { return paymentAmount; }
    }
}
