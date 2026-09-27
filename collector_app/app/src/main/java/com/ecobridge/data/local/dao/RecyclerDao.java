package com.ecobridge.data.local.dao;

import androidx.lifecycle.LiveData;
import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;

import com.ecobridge.data.local.entity.RecyclerEntity;

import java.util.List;

@Dao
public interface RecyclerDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insertRecyclers(List<RecyclerEntity> recyclers);

    @Query("SELECT * FROM recyclers ORDER BY defaultRatePerKg DESC")
    LiveData<List<RecyclerEntity>> getAllRecyclersLiveData();

    @Query("SELECT * FROM recyclers ORDER BY defaultRatePerKg DESC")
    List<RecyclerEntity> getAllRecyclersList();

    @Query("SELECT * FROM recyclers WHERE uuid = :uuid LIMIT 1")
    RecyclerEntity getRecyclerByUuid(String uuid);

    @Query("SELECT COUNT(*) FROM recyclers")
    int getRecyclersCount();
}
