package com.ecobridge.data.repository;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;

import androidx.lifecycle.LiveData;

import com.ecobridge.data.local.AppDatabase;
import com.ecobridge.data.local.entity.HandoverEntity;
import com.ecobridge.data.local.entity.LotEntity;
import com.ecobridge.data.local.entity.LotPhotoEntity;
import com.ecobridge.data.local.entity.PriceEntity;
import com.ecobridge.data.local.entity.RecyclerEntity;

import java.util.List;

/**
 * EcoBridgeRepository
 * Single source of truth coordinating local Room database operations,
 * background threading, and network synchronization triggers.
 */
public class EcoBridgeRepository {

    private final AppDatabase database;
    private final Context context;
    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    public interface OnLotCreatedCallback {
        void onSuccess(LotEntity lot);
        void onError(Exception e);
    }

    public interface OnHandoverCreatedCallback {
        void onSuccess(HandoverEntity handover);
        void onError(Exception e);
    }

    public interface OnPriceLoadedCallback {
        void onLoaded(PriceEntity price);
    }

    public interface OnRecyclersLoadedCallback {
        void onLoaded(List<RecyclerEntity> recyclers);
    }

    public interface OnLotLoadedCallback {
        void onLoaded(LotEntity lot);
    }

    public interface OnLotsLoadedCallback {
        void onLoaded(List<LotEntity> lots);
    }

    public interface OnPricesLoadedCallback {
        void onLoaded(List<PriceEntity> prices);
    }

    public interface OnEarningsSummaryCallback {
        void onLoaded(EarningsSummary summary);
    }

    public static class EarningsSummary {
        public double todayEarnings;
        public double weeklyEarnings;
        public double totalEarnings;
        public int totalLots;
        public double totalWeight;

        public EarningsSummary(double todayEarnings, double weeklyEarnings, double totalEarnings, 
                              int totalLots, double totalWeight) {
            this.todayEarnings = todayEarnings;
            this.weeklyEarnings = weeklyEarnings;
            this.totalEarnings = totalEarnings;
            this.totalLots = totalLots;
            this.totalWeight = totalWeight;
        }
    }

    public EcoBridgeRepository(AppDatabase database, Context context) {
        this.database = database;
        this.context = context.getApplicationContext();
    }

    // --- LiveData Streams ---

    public LiveData<List<LotEntity>> getAllLots() {
        return database.lotDao().getAllLotsLiveData();
    }

    public LiveData<List<PriceEntity>> getAllPrices() {
        return database.priceDao().getAllPricesLiveData();
    }

    public LiveData<List<RecyclerEntity>> getAllRecyclers() {
        return database.recyclerDao().getAllRecyclersLiveData();
    }

    public LiveData<List<HandoverEntity>> getAllHandovers() {
        return database.handoverDao().getAllHandoversLiveData();
    }

    public LiveData<Integer> getPendingSyncCount() {
        return database.lotDao().getPendingLotsCountLiveData();
    }

    public LiveData<Integer> getTotalLotsCount() {
        return database.lotDao().getTotalLotsCountLiveData();
    }

    public LiveData<Double> getTotalWeightSold() {
        return database.lotDao().getTotalWeightSoldLiveData();
    }

    public LiveData<Double> getLifetimeEarnings() {
        return database.handoverDao().getTotalLifetimeEarningsLiveData();
    }

    public LiveData<Double> getTodayEarnings(String datePrefix) {
        return database.handoverDao().getTodayEarningsLiveData(datePrefix);
    }

    // --- Data Operations (Off Main Thread) ---

    public void createLot(final LotEntity lot, final LotPhotoEntity photo, final OnLotCreatedCallback callback) {
        AppDatabase.databaseWriteExecutor.execute(() -> {
            try {
                database.lotDao().insertLot(lot);
                if (photo != null) {
                    database.lotPhotoDao().insertPhoto(photo);
                }
                if (callback != null) {
                    mainHandler.post(() -> callback.onSuccess(lot));
                }
            } catch (Exception e) {
                if (callback != null) {
                    mainHandler.post(() -> callback.onError(e));
                }
            }
        });
    }

    public void createHandover(final HandoverEntity handover, final OnHandoverCreatedCallback callback) {
        AppDatabase.databaseWriteExecutor.execute(() -> {
            try {
                database.handoverDao().insertHandover(handover);
                // Transition lot status to HANDOVER_CONFIRMED
                database.lotDao().updateLotStatus(
                        handover.getLotId(),
                        "HANDOVER_CONFIRMED",
                        DemoDataSeeder.getUtcTimestamp()
                );
                if (callback != null) {
                    mainHandler.post(() -> callback.onSuccess(handover));
                }
            } catch (Exception e) {
                if (callback != null) {
                    mainHandler.post(() -> callback.onError(e));
                }
            }
        });
    }

    public void getPriceForCategory(final String category, final OnPriceLoadedCallback callback) {
        AppDatabase.databaseWriteExecutor.execute(() -> {
            PriceEntity price = database.priceDao().getPriceForCategory(category);
            if (callback != null) {
                mainHandler.post(() -> callback.onLoaded(price));
            }
        });
    }

    public void getRecyclersList(final OnRecyclersLoadedCallback callback) {
        AppDatabase.databaseWriteExecutor.execute(() -> {
            List<RecyclerEntity> recyclers = database.recyclerDao().getAllRecyclersList();
            if (callback != null) {
                mainHandler.post(() -> callback.onLoaded(recyclers));
            }
        });
    }

    public void getLotByUuid(final String uuid, final OnLotLoadedCallback callback) {
        AppDatabase.databaseWriteExecutor.execute(() -> {
            LotEntity lot = database.lotDao().getLotByUuid(uuid);
            if (callback != null) {
                mainHandler.post(() -> callback.onLoaded(lot));
            }
        });
    }

    public void getLotByShortCode(final String shortCode, final OnLotLoadedCallback callback) {
        AppDatabase.databaseWriteExecutor.execute(() -> {
            LotEntity lot = database.lotDao().getLotByShortCode(shortCode);
            if (callback != null) {
                mainHandler.post(() -> callback.onLoaded(lot));
            }
        });
    }

    public void getAllLots(final OnLotsLoadedCallback callback) {
        AppDatabase.databaseWriteExecutor.execute(() -> {
            List<LotEntity> lots = database.lotDao().getAllLotsList();
            if (callback != null) {
                mainHandler.post(() -> callback.onLoaded(lots));
            }
        });
    }

    public void getAllPrices(final OnPricesLoadedCallback callback) {
        AppDatabase.databaseWriteExecutor.execute(() -> {
            List<PriceEntity> prices = database.priceDao().getAllPricesList();
            if (callback != null) {
                mainHandler.post(() -> callback.onLoaded(prices));
            }
        });
    }

    public void getEarningsSummary(final OnEarningsSummaryCallback callback) {
        AppDatabase.databaseWriteExecutor.execute(() -> {
            // Get today's date prefix for filtering
            String todayDatePrefix = new java.text.SimpleDateFormat("yyyy-MM-dd", java.util.Locale.US)
                    .format(new java.util.Date());

            // Get basic stats
            Integer totalLots = database.lotDao().getTotalLotsCount();
            Double totalWeight = database.lotDao().getTotalWeightSold();
            Double totalEarnings = database.handoverDao().getTotalLifetimeEarnings();
            Double todayEarnings = database.handoverDao().getTodayEarnings(todayDatePrefix);

            // For weekly earnings, we'll use a simplified approach (same as total for now)
            // In production, this would filter by date range
            double weeklyEarnings = totalEarnings != null ? totalEarnings : 0.0;

            EarningsSummary summary = new EarningsSummary(
                    todayEarnings != null ? todayEarnings : 0.0,
                    weeklyEarnings,
                    totalEarnings != null ? totalEarnings : 0.0,
                    totalLots != null ? totalLots : 0,
                    totalWeight != null ? totalWeight : 0.0
            );

            if (callback != null) {
                mainHandler.post(() -> callback.onLoaded(summary));
            }
        });
    }
}
