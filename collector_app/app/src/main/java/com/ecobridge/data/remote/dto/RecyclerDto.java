package com.ecobridge.data.remote.dto;

import com.google.gson.annotations.SerializedName;

public class RecyclerDto {

    @SerializedName("uuid")
    private String uuid;

    @SerializedName("name")
    private String name;

    @SerializedName("cpcb_registration_no")
    private String cpcbRegistrationNo;

    @SerializedName("latitude")
    private double latitude;

    @SerializedName("longitude")
    private double longitude;

    @SerializedName("verification_status")
    private String verificationStatus;

    @SerializedName("default_rate_per_kg")
    private double defaultRatePerKg;

    @SerializedName("distance_km")
    private double distanceKm;

    public String getUuid() { return uuid; }
    public void setUuid(String uuid) { this.uuid = uuid; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getCpcbRegistrationNo() { return cpcbRegistrationNo; }
    public void setCpcbRegistrationNo(String cpcbRegistrationNo) { this.cpcbRegistrationNo = cpcbRegistrationNo; }

    public double getLatitude() { return latitude; }
    public void setLatitude(double latitude) { this.latitude = latitude; }

    public double getLongitude() { return longitude; }
    public void setLongitude(double longitude) { this.longitude = longitude; }

    public String getVerificationStatus() { return verificationStatus; }
    public void setVerificationStatus(String verificationStatus) { this.verificationStatus = verificationStatus; }

    public double getDefaultRatePerKg() { return defaultRatePerKg; }
    public void setDefaultRatePerKg(double defaultRatePerKg) { this.defaultRatePerKg = defaultRatePerKg; }

    public double getDistanceKm() { return distanceKm; }
    public void setDistanceKm(double distanceKm) { this.distanceKm = distanceKm; }
}
