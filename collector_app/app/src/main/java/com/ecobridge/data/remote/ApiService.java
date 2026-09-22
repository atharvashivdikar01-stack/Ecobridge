package com.ecobridge.data.remote;

import com.ecobridge.data.remote.dto.ApiResponseDto;
import com.ecobridge.data.remote.dto.BatchSyncRequest;
import com.ecobridge.data.remote.dto.BatchSyncResponse;
import com.ecobridge.data.remote.dto.HandoverDto;
import com.ecobridge.data.remote.dto.LotDto;
import com.ecobridge.data.remote.dto.PriceDto;
import com.ecobridge.data.remote.dto.RecyclerDto;

import java.util.List;

import retrofit2.Call;
import retrofit2.http.Body;
import retrofit2.http.GET;
import retrofit2.http.POST;

/**
 * ApiService
 * Retrofit REST endpoints adhering to the /api/v1 contract.
 */
public interface ApiService {

    @GET("api/v1/prices")
    Call<ApiResponseDto<List<PriceDto>>> getPrices();

    @GET("api/v1/recyclers")
    Call<ApiResponseDto<List<RecyclerDto>>> getRecyclers();

    @POST("api/v1/lots")
    Call<ApiResponseDto<LotDto>> createLot(@Body LotDto lot);

    @POST("api/v1/handovers")
    Call<ApiResponseDto<HandoverDto>> createHandover(@Body HandoverDto handover);

    @POST("api/v1/sync/batch")
    Call<ApiResponseDto<BatchSyncResponse>> syncBatch(@Body BatchSyncRequest batchRequest);

    @GET("api/v1/sync/status")
    Call<ApiResponseDto<Object>> getSyncStatus();
}
