package com.ecobridge.data.local.entity;

import androidx.annotation.NonNull;
import androidx.room.Entity;
import androidx.room.ForeignKey;
import androidx.room.Index;
import androidx.room.PrimaryKey;

/**
 * LotPhotoEntity
 * Stores metadata and cryptographic SHA-256 hash of scrap photos.
 */
@Entity(tableName = "lot_photos",
        foreignKeys = @ForeignKey(entity = LotEntity.class,
                parentColumns = "uuid",
                childColumns = "lotId",
                onDelete = ForeignKey.CASCADE),
        indices = {@Index("lotId"), @Index("syncStatus")})
public class LotPhotoEntity {

    @PrimaryKey
    @NonNull
    private String uuid;

    @NonNull
    private String lotId;

    private String sha256Hash;
    private String filePath;
    private String createdAt;
    private String syncStatus;

    public LotPhotoEntity(@NonNull String uuid, @NonNull String lotId,
                          String sha256Hash, String filePath, String createdAt, String syncStatus) {
        this.uuid = uuid;
        this.lotId = lotId;
        this.sha256Hash = sha256Hash;
        this.filePath = filePath;
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

    @NonNull
    public String getLotId() {
        return lotId;
    }

    public void setLotId(@NonNull String lotId) {
        this.lotId = lotId;
    }

    public String getSha256Hash() {
        return sha256Hash;
    }

    public void setSha256Hash(String sha256Hash) {
        this.sha256Hash = sha256Hash;
    }

    public String getFilePath() {
        return filePath;
    }

    public void setFilePath(String filePath) {
        this.filePath = filePath;
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
