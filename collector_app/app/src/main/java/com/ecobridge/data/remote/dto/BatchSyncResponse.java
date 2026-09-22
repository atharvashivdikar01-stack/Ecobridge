package com.ecobridge.data.remote.dto;

import com.google.gson.annotations.SerializedName;

import java.util.List;

public class BatchSyncResponse {

    @SerializedName("synced_lot_ids")
    private List<String> syncedLotIds;

    @SerializedName("synced_handover_ids")
    private List<String> syncedHandoverIds;

    @SerializedName("failed_items")
    private List<String> failedItems;

    public BatchSyncResponse() {}

    public List<String> getSyncedLotIds() { return syncedLotIds; }
    public void setSyncedLotIds(List<String> syncedLotIds) { this.syncedLotIds = syncedLotIds; }

    public List<String> getSyncedHandoverIds() { return syncedHandoverIds; }
    public void setSyncedHandoverIds(List<String> syncedHandoverIds) { this.syncedHandoverIds = syncedHandoverIds; }

    public List<String> getFailedItems() { return failedItems; }
    public void setFailedItems(List<String> failedItems) { this.failedItems = failedItems; }
}
