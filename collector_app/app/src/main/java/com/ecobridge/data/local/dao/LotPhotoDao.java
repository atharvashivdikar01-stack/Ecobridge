package com.ecobridge.data.local.dao;

import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;

import com.ecobridge.data.local.entity.LotPhotoEntity;

import java.util.List;

@Dao
public interface LotPhotoDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insertPhoto(LotPhotoEntity photo);

    @Query("SELECT * FROM lot_photos WHERE lotId = :lotId LIMIT 1")
    LotPhotoEntity getPhotoForLot(String lotId);

    @Query("SELECT * FROM lot_photos WHERE syncStatus = 'PENDING' OR syncStatus = 'FAILED'")
    List<LotPhotoEntity> getPendingPhotos();

    @Query("UPDATE lot_photos SET syncStatus = :syncStatus WHERE uuid = :uuid")
    void updateSyncStatus(String uuid, String syncStatus);
}
