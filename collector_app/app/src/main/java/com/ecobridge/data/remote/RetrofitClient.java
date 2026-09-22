package com.ecobridge.data.remote;

import java.util.concurrent.TimeUnit;

import okhttp3.OkHttpClient;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

/**
 * RetrofitClient
 * Configures HTTP client with timeouts, logging, and JSON converters.
 */
public class RetrofitClient {

    // Default to Android Emulator loopback to host Flask backend port 5000
    private static final String DEFAULT_BASE_URL = "http://10.0.2.2:5000/";
    private static Retrofit retrofit = null;

    public static ApiService getApiService() {
        return getClient(DEFAULT_BASE_URL).create(ApiService.class);
    }

    public static Retrofit getClient(String baseUrl) {
        if (retrofit == null) {
            HttpLoggingInterceptor logging = new HttpLoggingInterceptor();
            logging.setLevel(HttpLoggingInterceptor.Level.BODY);

            OkHttpClient client = new OkHttpClient.Builder()
                    .connectTimeout(15, TimeUnit.SECONDS)
                    .readTimeout(20, TimeUnit.SECONDS)
                    .writeTimeout(20, TimeUnit.SECONDS)
                    .addInterceptor(logging)
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
