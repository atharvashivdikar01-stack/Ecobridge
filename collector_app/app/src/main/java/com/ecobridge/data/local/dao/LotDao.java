package com.ecobridge.data.local.dao;

import androidx.lifecycle.LiveData;
import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;
import androidx.room.Update;

import com.ecobridge.data.local.entity.LotEntity;

import java.util.List;

@Dao
public interface LotDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insertLot(LotEntity lot);

    @Update
    void updateLot(LotEntity lot);

    @Query("SELECT * FROM lots WHERE uuid = :uuid LIMIT 1")
    LotEntity getLotByUuid(String uuid);

    @Query("SELECT * FROM lots WHERE shortCode = :shortCode LIMIT 1")
    LotEntity getLotByShortCode(String shortCode);

    @Query("SELECT * FROM lots ORDER BY createdAt DESC")
    LiveData<List<LotEntity>> getAllLotsLiveData();

    @Query("SELECT * FROM lots ORDER BY createdAt DESC")
    List<LotEntity> getAllLotsList();

    @Query("SELECT * FROM lots ORDER BY createdAt DESC")
    List<LotEntity> getAllLotsSync();

    @Query("SELECT * FROM lots WHERE syncStatus = 'PENDING' OR syncStatus = 'FAILED'")
    List<LotEntity> getPendingLots();

    @Query("SELECT COUNT(*) FROM lots WHERE syncStatus = 'PENDING' OR syncStatus = 'FAILED'")
    LiveData<Integer> getPendingLotsCountLiveData();

    @Query("UPDATE lots SET syncStatus = :syncStatus, updatedAt = :updatedAt WHERE uuid = :uuid")
    void updateSyncStatus(String uuid, String syncStatus, String updatedAt);

    @Query("UPDATE lots SET status = :newStatus, updatedAt = :updatedAt WHERE uuid = :uuid")
    void updateLotStatus(String uuid, String newStatus, String updatedAt);

    @Query("SELECT COUNT(*) FROM lots")
    LiveData<Integer> getTotalLotsCountLiveData();

    @Query("SELECT COUNT(*) FROM lots")
    Integer getTotalLotsCount();

    @Query("SELECT COALESCE(SUM(approxWeightKg), 0.0) FROM lots")
    LiveData<Double> getTotalWeightSoldLiveData();

    @Query("SELECT COALESCE(SUM(approxWeightKg), 0.0) FROM lots")
    Double getTotalWeightSold();
}
