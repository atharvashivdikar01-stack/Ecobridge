package com.ecobridge.data.local.dao;

import androidx.lifecycle.LiveData;
import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;

import com.ecobridge.data.local.entity.HandoverEntity;

import java.util.List;

@Dao
public interface HandoverDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insertHandover(HandoverEntity handover);

    @Query("SELECT * FROM handovers WHERE lotId = :lotId LIMIT 1")
    HandoverEntity getHandoverForLot(String lotId);

    @Query("SELECT * FROM handovers ORDER BY createdAt DESC")
    LiveData<List<HandoverEntity>> getAllHandoversLiveData();

    @Query("SELECT * FROM handovers WHERE syncStatus = 'PENDING' OR syncStatus = 'FAILED'")
    List<HandoverEntity> getPendingHandovers();

    @Query("UPDATE handovers SET syncStatus = :syncStatus WHERE uuid = :uuid")
    void updateSyncStatus(String uuid, String syncStatus);

    @Query("SELECT COALESCE(SUM(paymentAmount), 0.0) FROM handovers WHERE paymentStatus = 'PAID'")
    LiveData<Double> getTotalLifetimeEarningsLiveData();

    @Query("SELECT COALESCE(SUM(paymentAmount), 0.0) FROM handovers WHERE paymentStatus = 'PAID'")
    Double getTotalLifetimeEarnings();

    @Query("SELECT COALESCE(SUM(paymentAmount), 0.0) FROM handovers WHERE paymentStatus = 'PAID' AND createdAt LIKE :datePrefix || '%'")
    LiveData<Double> getTodayEarningsLiveData(String datePrefix);

    @Query("SELECT COALESCE(SUM(paymentAmount), 0.0) FROM handovers WHERE paymentStatus = 'PAID' AND createdAt LIKE :datePrefix || '%'")
    Double getTodayEarnings(String datePrefix);

    @Query("SELECT COUNT(*) FROM handovers WHERE syncStatus = 'PENDING' OR syncStatus = 'FAILED'")
    LiveData<Integer> getPendingHandoversCountLiveData();
}
