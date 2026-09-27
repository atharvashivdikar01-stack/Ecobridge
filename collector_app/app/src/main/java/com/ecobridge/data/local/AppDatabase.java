package com.ecobridge.data.local;

import android.content.Context;

import androidx.annotation.NonNull;
import androidx.room.Database;
import androidx.room.Room;
import androidx.room.RoomDatabase;
import androidx.room.migration.Migration;
import androidx.sqlite.db.SupportSQLiteDatabase;

import com.ecobridge.data.local.dao.CollectorDao;
import com.ecobridge.data.local.dao.HandoverDao;
import com.ecobridge.data.local.dao.LotDao;
import com.ecobridge.data.local.dao.LotPhotoDao;
import com.ecobridge.data.local.dao.PriceDao;
import com.ecobridge.data.local.dao.RecyclerDao;
import com.ecobridge.data.local.entity.CollectorEntity;
import com.ecobridge.data.local.entity.HandoverEntity;
import com.ecobridge.data.local.entity.LotEntity;
import com.ecobridge.data.local.entity.LotPhotoEntity;
import com.ecobridge.data.local.entity.PriceEntity;
import com.ecobridge.data.local.entity.RecyclerEntity;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * AppDatabase
 * Room database definition managing local SQLite tables for offline-first resilience.
 */
@Database(
        entities = {
                CollectorEntity.class,
                LotEntity.class,
                LotPhotoEntity.class,
                HandoverEntity.class,
                PriceEntity.class,
                RecyclerEntity.class
        },
        version = 2,
        exportSchema = false
)
public abstract class AppDatabase extends RoomDatabase {

    private static final String DATABASE_NAME = "ecobridge_collector.db";
    private static volatile AppDatabase INSTANCE;
    private static final int NUMBER_OF_THREADS = 4;
    public static final ExecutorService databaseWriteExecutor =
            Executors.newFixedThreadPool(NUMBER_OF_THREADS);

    public static final Migration MIGRATION_1_2 = new Migration(1, 2) {
        @Override
        public void migrate(@NonNull SupportSQLiteDatabase database) {
            database.execSQL("ALTER TABLE lots ADD COLUMN aiCategory TEXT");
            database.execSQL("ALTER TABLE lots ADD COLUMN aiConfidence REAL NOT NULL DEFAULT 0.0");
            database.execSQL("ALTER TABLE lots ADD COLUMN collectorConfirmedCategory TEXT");
            database.execSQL("ALTER TABLE lots ADD COLUMN aiModelVersion TEXT");
            database.execSQL("ALTER TABLE lots ADD COLUMN imageHash TEXT");
        }
    };

    public abstract CollectorDao collectorDao();
    public abstract LotDao lotDao();
    public abstract LotPhotoDao lotPhotoDao();
    public abstract HandoverDao handoverDao();
    public abstract PriceDao priceDao();
    public abstract RecyclerDao recyclerDao();

    public static AppDatabase getInstance(final Context context) {
        if (INSTANCE == null) {
            synchronized (AppDatabase.class) {
                if (INSTANCE == null) {
                    INSTANCE = Room.databaseBuilder(
                                    context.getApplicationContext(),
                                    AppDatabase.class,
                                    DATABASE_NAME
                            )
                            .addMigrations(MIGRATION_1_2)
                            .build();
                }
            }
        }
        return INSTANCE;
    }
}
