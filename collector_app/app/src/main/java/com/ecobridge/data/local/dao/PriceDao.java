package com.ecobridge.data.local.dao;

import androidx.lifecycle.LiveData;
import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;

import com.ecobridge.data.local.entity.PriceEntity;

import java.util.List;

@Dao
public interface PriceDao {

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insertPrices(List<PriceEntity> prices);

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insertOrUpdatePrice(PriceEntity price);

    @Query("SELECT * FROM prices WHERE category = :category LIMIT 1")
    PriceEntity getPriceForCategory(String category);

    @Query("SELECT * FROM prices ORDER BY category ASC")
    LiveData<List<PriceEntity>> getAllPricesLiveData();

    @Query("SELECT * FROM prices ORDER BY category ASC")
    List<PriceEntity> getAllPricesList();

    @Query("SELECT COUNT(*) FROM prices")
    int getPricesCount();
}
