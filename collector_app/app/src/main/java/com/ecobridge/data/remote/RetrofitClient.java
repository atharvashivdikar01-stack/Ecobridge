package com.ecobridge.data.remote;

import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;
import com.ecobridge.BuildConfig;
import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.data.local.TokenStore;
import okhttp3.Request;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

/**
 * RetrofitClient
 * Configures HTTP client with timeouts, logging, and JSON converters.
 */
public class RetrofitClient {

    private static Retrofit retrofit = null;

    public static ApiService getApiService() {
        return getClient(BuildConfig.API_BASE_URL).create(ApiService.class);
    }

    public static Retrofit getClient(String baseUrl) {
        if (retrofit == null) {
            OkHttpClient client = new OkHttpClient.Builder()
                    .connectTimeout(15, TimeUnit.SECONDS)
                    .readTimeout(20, TimeUnit.SECONDS)
                    .writeTimeout(20, TimeUnit.SECONDS)
                    .addInterceptor(chain -> {
                        Request request = chain.request();
                        String token = TokenStore.accessToken(EcoBridgeApplication.getInstance());
                        return chain.proceed(token == null ? request : request.newBuilder()
                                .header("Authorization", "Bearer " + token).build());
                    })
                    .build();

            retrofit = new Retrofit.Builder()
                    .baseUrl(baseUrl)
                    .client(client)
                    .addConverterFactory(GsonConverterFactory.create())
                    .build();
        }
        return retrofit;
    }
}
