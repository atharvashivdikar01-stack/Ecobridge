package com.ecobridge.data.remote.dto;

import com.google.gson.annotations.SerializedName;

import java.util.List;

public class BatchSyncRequest {

    @SerializedName("collector_uuid")
    private String collectorUuid;

    @SerializedName("lots")
    private List<LotDto> lots;

    @SerializedName("handovers")
    private List<HandoverDto> handovers;

    public BatchSyncRequest() {}

    public BatchSyncRequest(String collectorUuid, List<LotDto> lots, List<HandoverDto> handovers) {
        this.collectorUuid = collectorUuid;
        this.lots = lots;
        this.handovers = handovers;
    }

    public String getCollectorUuid() { return collectorUuid; }
    public void setCollectorUuid(String collectorUuid) { this.collectorUuid = collectorUuid; }

    public List<LotDto> getLots() { return lots; }
    public void setLots(List<LotDto> lots) { this.lots = lots; }

    public List<HandoverDto> getHandovers() { return handovers; }
    public void setHandovers(List<HandoverDto> handovers) { this.handovers = handovers; }
}
