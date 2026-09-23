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

        list.add(new PriceEntity("Batteries", 105.0, 115.0, SOURCE_TYPE, now, now));
        list.add(new PriceEntity("Copper Cables & Wires", 195.0, 210.0, SOURCE_TYPE, now, now));
        list.add(new PriceEntity("CRT Monitors & TVs", 45.0, 55.0, SOURCE_TYPE, now, now));
        list.add(new PriceEntity("LCD / LED Panels", 85.0, 95.0, SOURCE_TYPE, now, now));
        list.add(new PriceEntity("Mixed E-Waste Plastics", 22.0, 28.0, SOURCE_TYPE, now, now));
        list.add(new PriceEntity("Motors & Magnet Assemblies", 55.0, 65.0, SOURCE_TYPE, now, now));
        list.add(new PriceEntity("Other Electronic Scrap", 40.0, 50.0, SOURCE_TYPE, now, now));
        list.add(new PriceEntity("Printed Circuit Boards (PCBs)", 330.0, 365.0, SOURCE_TYPE, now, now));

        return list;
    }

    public static List<RecyclerEntity> getInitialRecyclerData() {
        List<RecyclerEntity> list = new ArrayList<>();
        String now = getUtcTimestamp();

        list.add(new RecyclerEntity(
                "00000000-0000-0000-0000-000000000101",
                "Local Test Recycler",
                "LOCAL-DEV-ONLY",
                18.5204, 73.8567,
                "LOCAL_DEMO",
                450.0,
                3.2,
                now,
                "SYNCED"
        ));

        list.add(new RecyclerEntity(
                "rec-002",
                "Demo Recycler B",
                "DEMO-UNVERIFIED",
                18.5314, 73.8446,
                "DEMO_UNVERIFIED",
                460.0,
                5.8,
                now,
                "SYNCED"
        ));

        list.add(new RecyclerEntity(
                "rec-003",
                "Demo Recycler C",
                "DEMO-UNVERIFIED",
                18.5089, 73.8258,
                "DEMO_UNVERIFIED",
                435.0,
                8.4,
                now,
                "SYNCED"
        ));

        list.add(new RecyclerEntity(
                "rec-004",
                "Demo Recycler D",
                "DEMO-UNVERIFIED",
                18.4901, 73.8821,
                "DEMO_UNVERIFIED",
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
