package com.ecobridge.data.remote;

import com.ecobridge.data.remote.dto.ApiResponseDto;
import com.ecobridge.data.remote.dto.BatchSyncRequest;
import com.ecobridge.data.remote.dto.BatchSyncResponse;
import com.ecobridge.data.remote.dto.HandoverDto;
import com.ecobridge.data.remote.dto.LotDto;
import com.ecobridge.data.remote.dto.OtpRequest;
import com.ecobridge.data.remote.dto.TokenResponseDto;
import com.ecobridge.data.remote.dto.VerifyOtpRequest;
import com.ecobridge.data.remote.dto.SyncStatusResponse;

import retrofit2.Call;
import okhttp3.RequestBody;
import retrofit2.http.Body;
import retrofit2.http.GET;
import retrofit2.http.POST;
import retrofit2.http.Header;
import retrofit2.http.Path;

/**
 * ApiService
 * Retrofit REST endpoints adhering to the /api/v1 contract.
 */
public interface ApiService {
    @POST("api/v1/auth/otp/send")
    Call<ApiResponseDto<Object>> sendOtp(@Body OtpRequest request);

    @POST("api/v1/auth/otp/verify")
    Call<ApiResponseDto<TokenResponseDto>> verifyOtp(@Body VerifyOtpRequest request);

    @POST("api/v1/sync/batch")
    Call<ApiResponseDto<BatchSyncResponse>> syncBatch(@Body BatchSyncRequest batchRequest);

    @POST("api/v1/sync/handovers")
    Call<ApiResponseDto<BatchSyncResponse>> syncHandovers(@Body BatchSyncRequest batchRequest);

    @POST("api/v1/lots/{lotId}/photos")
    Call<ApiResponseDto<Object>> uploadPhoto(@Path("lotId") String lotId,
                                               @Header("X-Image-SHA256") String sha256,
                                               @Header("Content-Type") String contentType,
                                               @Body RequestBody photo);

    @GET("api/v1/sync/status")
    Call<ApiResponseDto<SyncStatusResponse>> getSyncStatus();
}
