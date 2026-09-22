package com.ecobridge.data.repository;

import android.util.Log;

import com.ecobridge.data.local.AppDatabase;
import com.ecobridge.data.local.entity.PriceEntity;
import com.ecobridge.data.local.entity.RecyclerEntity;

import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.TimeZone;

/**
 * DemoDataSeeder
 * Pre-populates the local Room database with transparent benchmark scrap prices
 * and CPCB-registered certified recyclers for offline functionality and SIH demonstrations.
 * All demo records are explicitly marked as DEMO_DATASET.
 */
public class DemoDataSeeder {

    private static final String TAG = "DemoDataSeeder";
    private static final String SOURCE_TYPE = "DEMO_DATASET";

    public static void seedInitialDataIfEmpty(final AppDatabase database) {
        AppDatabase.databaseWriteExecutor.execute(() -> {
            try {
                int priceCount = database.priceDao().getPricesCount();
                if (priceCount == 0) {
                    Log.i(TAG, "Prices table empty. Seeding benchmark scrap price data...");
                    List<PriceEntity> initialPrices = getInitialPriceData();
                    database.priceDao().insertPrices(initialPrices);
                    Log.i(TAG, "Successfully seeded " + initialPrices.size() + " scrap price benchmarks.");
                }

                int recyclerCount = database.recyclerDao().getRecyclersCount();
                if (recyclerCount == 0) {
                    Log.i(TAG, "Recyclers table empty. Seeding verified recycler facilities...");
                    List<RecyclerEntity> initialRecyclers = getInitialRecyclerData();
                    database.recyclerDao().insertRecyclers(initialRecyclers);
                    Log.i(TAG, "Successfully seeded " + initialRecyclers.size() + " verified recyclers.");
                }
            } catch (Exception e) {
                Log.e(TAG, "Error seeding initial demo data: " + e.getMessage(), e);
            }
        });
    }

    public static List<PriceEntity> getInitialPriceData() {
        List<PriceEntity> list = new ArrayList<>();
        String now = getUtcTimestamp();

        list.add(new PriceEntity("Copper", 420.0, 450.0, SOURCE_TYPE, now, now));
        list.add(new PriceEntity("Aluminium", 145.0, 165.0, SOURCE_TYPE, now, now));
        list.add(new PriceEntity("Iron", 32.0, 38.0, SOURCE_TYPE, now, now));
        list.add(new PriceEntity("Printed Circuit Board (PCB)", 330.0, 365.0, SOURCE_TYPE, now, now));
        list.add(new PriceEntity("Mobile Phone", 280.0, 320.0, SOURCE_TYPE, now, now));
        list.add(new PriceEntity("Computer / Laptop", 350.0, 390.0, SOURCE_TYPE, now, now));
        list.add(new PriceEntity("Cables & Wire", 180.0, 210.0, SOURCE_TYPE, now, now));
        list.add(new PriceEntity("Batteries", 95.0, 115.0, SOURCE_TYPE, now, now));
        list.add(new PriceEntity("Mixed E-Waste", 75.0, 90.0, SOURCE_TYPE, now, now));
        list.add(new PriceEntity("Other Scrap", 40.0, 50.0, SOURCE_TYPE, now, now));

        return list;
    }

    public static List<RecyclerEntity> getInitialRecyclerData() {
        List<RecyclerEntity> list = new ArrayList<>();
        String now = getUtcTimestamp();

        list.add(new RecyclerEntity(
                "rec-001",
                "EcoRecycle India Pvt Ltd",
                "CPCB/EW-MH-2024-0012",
                18.5204, 73.8567,
                "VERIFIED_CPCB",
                450.0,
                3.2,
                now,
                "SYNCED"
        ));

        list.add(new RecyclerEntity(
                "rec-002",
                "Western India E-Waste Solutions",
                "CPCB/EW-MH-2023-0489",
                18.5314, 73.8446,
                "VERIFIED_CPCB",
                460.0,
                5.8,
                now,
                "SYNCED"
        ));

        list.add(new RecyclerEntity(
                "rec-003",
                "Maharashtra Clean Tech Dismantlers",
                "CPCB/EW-MH-2022-0911",
                18.5089, 73.8258,
                "VERIFIED_CPCB",
                435.0,
                8.4,
                now,
                "SYNCED"
        ));

        list.add(new RecyclerEntity(
                "rec-004",
                "Pune Green Earth Aggregators",
                "SPCB/AUTH-EW-2025-0104",
                18.4901, 73.8821,
                "VERIFIED_CPCB",
                425.0,
                11.2,
                now,
                "SYNCED"
        ));

        return list;
    }

    public static String getUtcTimestamp() {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US);
        sdf.setTimeZone(TimeZone.getTimeZone("UTC"));
        return sdf.format(new Date());
    }
}
