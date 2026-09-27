package com.ecobridge.data.local.dao;

import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;
import androidx.room.Update;

import com.ecobridge.data.local.entity.CollectorEntity;

@Dao
public interface CollectorDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insertOrUpdate(CollectorEntity collector);

    @Query("SELECT * FROM collectors LIMIT 1")
    CollectorEntity getCollector();

    @Update
    void update(CollectorEntity collector);
}
