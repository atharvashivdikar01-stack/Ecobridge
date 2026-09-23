package com.ecobridge.data.local.entity;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

/**
 * CollectorEntity
 * Represents the device's informal waste picker / aggregator profile.
 */
@Entity(tableName = "collectors")
public class CollectorEntity {

    @PrimaryKey
    @NonNull
    private String uuid;

    private String language;
    private String operatingArea;
    private String createdAt;
    private String updatedAt;
    private String syncStatus; // PENDING, SYNCING, SYNCED, FAILED

    public CollectorEntity(@NonNull String uuid, String language, String operatingArea,
                           String createdAt, String updatedAt, String syncStatus) {
        this.uuid = uuid;
        this.language = language;
        this.operatingArea = operatingArea;
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

    public String getLanguage() {
        return language;
    }

    public void setLanguage(String language) {
        this.language = language;
    }

    public String getOperatingArea() {
        return operatingArea;
    }

    public void setOperatingArea(String operatingArea) {
        this.operatingArea = operatingArea;
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
