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
import com.ecobridge.data.local.TokenStore;
import com.ecobridge.data.local.entity.HandoverEntity;
import com.ecobridge.data.local.entity.LotEntity;
import com.ecobridge.data.remote.ApiService;
import com.ecobridge.data.remote.RetrofitClient;
import com.ecobridge.data.remote.dto.ApiResponseDto;
import com.ecobridge.data.remote.dto.BatchSyncRequest;
import com.ecobridge.data.remote.dto.BatchSyncResponse;
import com.ecobridge.data.remote.dto.HandoverDto;
import com.ecobridge.data.remote.dto.LotDto;
import com.ecobridge.data.remote.dto.SyncStatusResponse;
import com.ecobridge.data.repository.DemoDataSeeder;
import com.ecobridge.utils.NetworkUtils;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.io.File;

import okhttp3.MediaType;
import okhttp3.RequestBody;
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
        if (!TokenStore.hasAccessToken(context)) {
            Log.i(TAG, "Sync deferred until collector signs in; records remain local.");
            return Result.retry();
        }

        AppDatabase database = AppDatabase.getInstance(context);
        List<LotEntity> pendingLots = database.lotDao().getPendingLots();
        List<HandoverEntity> pendingHandovers = database.handoverDao().getPendingHandovers();

        Log.i(TAG, "Found " + pendingLots.size() + " lots and " + pendingHandovers.size() + " handovers to sync.");

        // Mark as SYNCING in local database
        String now = DemoDataSeeder.getUtcTimestamp();
        for (LotEntity lot : pendingLots) {
            database.lotDao().updateSyncStatus(lot.getUuid(), "SYNCING", now);
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

        ApiService apiService = RetrofitClient.getApiService();

        try {
            if (pendingLots.isEmpty() || syncLots(database, lotDtos, apiService)) {
                if (!syncPendingHandovers(database, pendingHandovers, apiService)) {
                    return Result.retry();
                }
                if (!syncPendingPhotos(database, apiService) || !pullServerStatus(database, apiService)) return Result.retry();
                Log.i(TAG, "Batch synchronization completed successfully.");
                return Result.success();
            } else {
                Log.w(TAG, "Lot sync was rejected; reverting local lots to FAILED.");
                markFailed(database, pendingLots);
                return Result.retry();
            }
        } catch (Exception e) {
            Log.e(TAG, "Network exception during batch sync: " + e.getMessage(), e);
            markFailed(database, pendingLots);
            return Result.retry();
        }
    }

    private boolean syncLots(AppDatabase database, List<LotDto> lots, ApiService apiService) throws Exception {
        Response<ApiResponseDto<BatchSyncResponse>> response = apiService.syncBatch(
                new BatchSyncRequest("collector-device-01", lots, new ArrayList<>())).execute();
        if (!response.isSuccessful() || response.body() == null || !response.body().isSuccess()) return false;
        BatchSyncResponse result = response.body().getData();
        if (result != null && result.getSyncedLotIds() != null) for (String lotId : result.getSyncedLotIds())
            database.lotDao().updateSyncStatus(lotId, "SYNCED", DemoDataSeeder.getUtcTimestamp());
        return true;
    }

    private boolean syncPendingPhotos(AppDatabase database, ApiService apiService) throws Exception {
        for (com.ecobridge.data.local.entity.LotPhotoEntity photo : database.lotPhotoDao().getPendingPhotos()) {
            LotEntity lot = database.lotDao().getLotByUuid(photo.getLotId());
            File file = new File(photo.getFilePath());
            if (lot == null || !file.isFile()) return false;
            Response<ApiResponseDto<Object>> response = apiService.uploadPhoto(lot.getShortCode(), photo.getSha256Hash(), "image/jpeg",
                    RequestBody.create(MediaType.parse("image/jpeg"), file)).execute();
            if (!response.isSuccessful() || response.body() == null || !response.body().isSuccess()) return false;
            database.lotPhotoDao().updateSyncStatus(photo.getUuid(), "SYNCED");
        }
        return true;
    }

    private boolean pullServerStatus(AppDatabase database, ApiService apiService) throws Exception {
        Response<ApiResponseDto<SyncStatusResponse>> response = apiService.getSyncStatus().execute();
        if (!response.isSuccessful() || response.body() == null || !response.body().isSuccess()) return false;
        SyncStatusResponse status = response.body().getData();
        if (status == null) return true;
        String now = DemoDataSeeder.getUtcTimestamp();
        if (status.getLots() != null) for (SyncStatusResponse.LotStatus lot : status.getLots())
            database.lotDao().updateLotStatusByShortCode(lot.getLotCode(), lot.getStatus(), now);
        if (status.getHandovers() != null) for (SyncStatusResponse.HandoverStatus handover : status.getHandovers())
            database.handoverDao().applyServerStatus(handover.getReferenceNo(), handover.getPaymentStatus(), handover.getPaymentAmount());
        return true;
    }

    private void markFailed(AppDatabase database, List<LotEntity> lots) {
        String now = DemoDataSeeder.getUtcTimestamp();
        for (LotEntity lot : lots) {
            database.lotDao().updateSyncStatus(lot.getUuid(), "FAILED", now);
        }
    }

    private boolean syncPendingHandovers(AppDatabase database, List<HandoverEntity> handovers,
                                         ApiService apiService) throws Exception {
        List<HandoverDto> handoverDtos = new ArrayList<>();
        for (HandoverEntity handover : handovers) {
            LotEntity lot = database.lotDao().getLotByUuid(handover.getLotId());
            if (lot == null) {
                Log.w(TAG, "Keeping handover " + handover.getReferenceNo() + " pending: lot is missing locally.");
                continue;
            }
            handoverDtos.add(new HandoverDto(
                    handover.getUuid(), handover.getReferenceNo(), handover.getLotId(), lot.getShortCode(),
                    handover.getRecyclerId(), handover.getWeight(), handover.getAgreedPrice(),
                    handover.getRecordHash(), handover.getPaymentMode(), handover.getPaymentAmount(),
                    handover.getPaymentStatus(), handover.getCreatedAt()
            ));
        }
        if (handoverDtos.isEmpty()) return true;

        Response<ApiResponseDto<BatchSyncResponse>> response = apiService.syncHandovers(
                new BatchSyncRequest("collector-device-01", new ArrayList<>(), handoverDtos)
        ).execute();
        if (!response.isSuccessful() || response.body() == null || !response.body().isSuccess()) {
            Log.w(TAG, "Handover sync failed with HTTP " + response.code());
            return false;
        }
        BatchSyncResponse result = response.body().getData();
        if (result != null && result.getSyncedHandoverIds() != null) {
            for (String handoverId : result.getSyncedHandoverIds()) {
                database.handoverDao().updateSyncStatus(handoverId, "SYNCED");
            }
        }
        return true;
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
