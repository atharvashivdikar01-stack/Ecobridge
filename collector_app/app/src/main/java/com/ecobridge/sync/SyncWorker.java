package com.ecobridge.sync;

import android.content.Context;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.work.Constraints;
import androidx.work.ExistingPeriodicWorkPolicy;
import androidx.work.ExistingWorkPolicy;
import androidx.work.NetworkType;
import androidx.work.OneTimeWorkRequest;
import androidx.work.PeriodicWorkRequest;
import androidx.work.WorkManager;
import androidx.work.Worker;
import androidx.work.WorkerParameters;

import com.ecobridge.data.local.AppDatabase;
import com.ecobridge.data.local.entity.HandoverEntity;
import com.ecobridge.data.local.entity.LotEntity;
import com.ecobridge.data.remote.ApiService;
import com.ecobridge.data.remote.RetrofitClient;
import com.ecobridge.data.remote.dto.ApiResponseDto;
import com.ecobridge.data.remote.dto.BatchSyncRequest;
import com.ecobridge.data.remote.dto.BatchSyncResponse;
import com.ecobridge.data.remote.dto.HandoverDto;
import com.ecobridge.data.remote.dto.LotDto;
import com.ecobridge.data.repository.DemoDataSeeder;
import com.ecobridge.utils.NetworkUtils;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

import retrofit2.Response;

/**
 * SyncWorker
 * WorkManager task that reads pending offline lots and handovers from Room,
 * batches them, sends them to POST /api/v1/sync/batch via Retrofit,
 * and marks successfully ingested entities as SYNCED with exponential backoff on errors.
 */
public class SyncWorker extends Worker {

    private static final String TAG = "SyncWorker";
    private static final String UNIQUE_PERIODIC_NAME = "EcoBridgePeriodicSync";
    private static final String UNIQUE_ONETIME_NAME = "EcoBridgeImmediateSync";

    public SyncWorker(@NonNull Context context, @NonNull WorkerParameters workerParams) {
        super(context, workerParams);
    }

    @NonNull
    @Override
    public Result doWork() {
        Context context = getApplicationContext();
        Log.i(TAG, "Starting EcoBridge WorkManager sync execution...");

        if (!NetworkUtils.isNetworkAvailable(context)) {
            Log.w(TAG, "No internet connectivity detected. Retrying sync with exponential backoff.");
            return Result.retry();
        }

        AppDatabase database = AppDatabase.getInstance(context);
        List<LotEntity> pendingLots = database.lotDao().getPendingLots();
        List<HandoverEntity> pendingHandovers = database.handoverDao().getPendingHandovers();

        if (pendingLots.isEmpty() && pendingHandovers.isEmpty()) {
            Log.i(TAG, "No pending offline records found in Room. Sync complete.");
            return Result.success();
        }

        Log.i(TAG, "Found " + pendingLots.size() + " lots and " + pendingHandovers.size() + " handovers to sync.");

        // Mark as SYNCING in local database
        String now = DemoDataSeeder.getUtcTimestamp();
        for (LotEntity lot : pendingLots) {
            database.lotDao().updateSyncStatus(lot.getUuid(), "SYNCING", now);
        }
        for (HandoverEntity ho : pendingHandovers) {
            database.handoverDao().updateSyncStatus(ho.getUuid(), "SYNCING");
        }

        // Map Room entities to Network DTOs
        List<LotDto> lotDtos = new ArrayList<>();
        for (LotEntity lot : pendingLots) {
            lotDtos.add(new LotDto(
                    lot.getUuid(),
                    lot.getShortCode(),
                    lot.getCategory(),
                    lot.getApproxWeightKg(),
                    lot.getQuotedPrice(),
                    lot.getNetEarnings(),
                    lot.getSelectedRecyclerId(),
                    lot.getStatus(),
                    lot.getCreatedAt()
            ));
        }

        List<HandoverDto> handoverDtos = new ArrayList<>();
        for (HandoverEntity ho : pendingHandovers) {
            handoverDtos.add(new HandoverDto(
                    ho.getUuid(),
                    ho.getReferenceNo(),
                    ho.getLotId(),
                    ho.getRecyclerId(),
                    ho.getWeight(),
                    ho.getAgreedPrice(),
                    ho.getRecordHash(),
                    ho.getPaymentMode(),
                    ho.getPaymentAmount(),
                    ho.getPaymentStatus(),
                    ho.getCreatedAt()
            ));
        }

        BatchSyncRequest batchRequest = new BatchSyncRequest("collector-device-01", lotDtos, handoverDtos);
        ApiService apiService = RetrofitClient.getApiService();

        try {
            Response<ApiResponseDto<BatchSyncResponse>> response = apiService.syncBatch(batchRequest).execute();
            if (response.isSuccessful() && response.body() != null && response.body().isSuccess()) {
                BatchSyncResponse result = response.body().getData();
                String syncedAt = DemoDataSeeder.getUtcTimestamp();

                // Mark synced lots as SYNCED
                if (result != null && result.getSyncedLotIds() != null) {
                    for (String lotId : result.getSyncedLotIds()) {
                        database.lotDao().updateSyncStatus(lotId, "SYNCED", syncedAt);
                    }
                } else {
                    for (LotEntity lot : pendingLots) {
                        database.lotDao().updateSyncStatus(lot.getUuid(), "SYNCED", syncedAt);
                    }
                }

                // Mark synced handovers as SYNCED
                if (result != null && result.getSyncedHandoverIds() != null) {
                    for (String hoId : result.getSyncedHandoverIds()) {
                        database.handoverDao().updateSyncStatus(hoId, "SYNCED");
                    }
                } else {
                    for (HandoverEntity ho : pendingHandovers) {
                        database.handoverDao().updateSyncStatus(ho.getUuid(), "SYNCED");
                    }
                }

                Log.i(TAG, "Batch synchronization completed successfully.");
                return Result.success();
            } else {
                Log.w(TAG, "Server responded with error code " + response.code() + ", reverting to FAILED.");
                markFailed(database, pendingLots, pendingHandovers);
                return Result.retry();
            }
        } catch (Exception e) {
            Log.e(TAG, "Network exception during batch sync: " + e.getMessage(), e);
            markFailed(database, pendingLots, pendingHandovers);
            return Result.retry();
        }
    }

    private void markFailed(AppDatabase database, List<LotEntity> lots, List<HandoverEntity> handovers) {
        String now = DemoDataSeeder.getUtcTimestamp();
        for (LotEntity lot : lots) {
            database.lotDao().updateSyncStatus(lot.getUuid(), "FAILED", now);
        }
        for (HandoverEntity ho : handovers) {
            database.handoverDao().updateSyncStatus(ho.getUuid(), "FAILED");
        }
    }

    /**
     * Triggers an immediate one-time sync request.
     */
    public static void triggerImmediateSync(Context context) {
        Constraints constraints = new Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build();

        OneTimeWorkRequest syncRequest = new OneTimeWorkRequest.Builder(SyncWorker.class)
                .setConstraints(constraints)
                .build();

        WorkManager.getInstance(context).enqueueUniqueWork(
                UNIQUE_ONETIME_NAME,
                ExistingWorkPolicy.REPLACE,
                syncRequest
        );
    }

    /**
     * Schedules periodic background sync (every 15 minutes when connected).
     */
    public static void schedulePeriodicSync(Context context) {
        Constraints constraints = new Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build();

        PeriodicWorkRequest periodicRequest = new PeriodicWorkRequest.Builder(
                SyncWorker.class,
                15, TimeUnit.MINUTES
        )
                .setConstraints(constraints)
                .build();

        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                UNIQUE_PERIODIC_NAME,
                ExistingPeriodicWorkPolicy.KEEP,
                periodicRequest
        );
    }
}
