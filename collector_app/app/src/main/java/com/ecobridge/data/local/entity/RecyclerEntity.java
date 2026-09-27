package com.ecobridge.data.local.entity;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

/**
 * RecyclerEntity
 * Stores authorized / verified recyclers cached on the device
 * to enable instant matching and transport cost calculation offline.
 */
@Entity(tableName = "recyclers")
public class RecyclerEntity {

    @PrimaryKey
    @NonNull
    private String uuid;

    private String name;
    private String cpcbRegistrationNo;
    private double latitude;
    private double longitude;
    private String verificationStatus; // "VERIFIED_CPCB", "AUTHORIZED_SPCB"
    private double defaultRatePerKg;
    private double distanceKm; // Cached or estimated distance
    private String updatedAt;
    private String syncStatus;

    public RecyclerEntity(@NonNull String uuid, String name, String cpcbRegistrationNo,
                          double latitude, double longitude, String verificationStatus,
                          double defaultRatePerKg, double distanceKm, String updatedAt, String syncStatus) {
        this.uuid = uuid;
        this.name = name;
        this.cpcbRegistrationNo = cpcbRegistrationNo;
        this.latitude = latitude;
        this.longitude = longitude;
        this.verificationStatus = verificationStatus;
        this.defaultRatePerKg = defaultRatePerKg;
        this.distanceKm = distanceKm;
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

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getCpcbRegistrationNo() {
        return cpcbRegistrationNo;
    }

    public void setCpcbRegistrationNo(String cpcbRegistrationNo) {
        this.cpcbRegistrationNo = cpcbRegistrationNo;
    }

    public double getLatitude() {
        return latitude;
    }

    public void setLatitude(double latitude) {
        this.latitude = latitude;
    }

    public double getLongitude() {
        return longitude;
    }

    public void setLongitude(double longitude) {
        this.longitude = longitude;
    }

    public String getVerificationStatus() {
        return verificationStatus;
    }

    public void setVerificationStatus(String verificationStatus) {
        this.verificationStatus = verificationStatus;
    }

    public double getDefaultRatePerKg() {
        return defaultRatePerKg;
    }

    public void setDefaultRatePerKg(double defaultRatePerKg) {
        this.defaultRatePerKg = defaultRatePerKg;
    }

    public double getDistanceKm() {
        return distanceKm;
    }

    public void setDistanceKm(double distanceKm) {
        this.distanceKm = distanceKm;
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
