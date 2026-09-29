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
    private static String cachedBaseUrl = null;

    public static String getBaseUrl() {
        try {
            android.content.SharedPreferences prefs = EcoBridgeApplication.getInstance()
                    .getSharedPreferences("ecobridge_prefs", android.content.Context.MODE_PRIVATE);
            String customUrl = prefs.getString("pref_server_url", null);
            if (customUrl != null && !customUrl.trim().isEmpty()) {
                if (customUrl.contains("10.0.2.2")) {
                    // Stale emulator URL from previous development session - purge it!
                    prefs.edit().remove("pref_server_url").apply();
                } else {
                    String clean = customUrl.trim().replaceAll("/api/v1/?$", "");
                    return clean.endsWith("/") ? clean : clean + "/";
                }
            }
        } catch (Throwable ignored) {}

        String url = BuildConfig.API_BASE_URL;
        if (url == null || url.trim().isEmpty() || url.contains("10.0.2.2")) {
            url = "https://ecobridge-api-sih26-d3hfbccrg3fpddcr.centralindia-01.azurewebsites.net/";
        }
        String clean = url.replaceAll("/api/v1/?$", "");
        return clean.endsWith("/") ? clean : clean + "/";
    }

    public static void setCustomBaseUrl(String url) {
        try {
            android.content.SharedPreferences prefs = EcoBridgeApplication.getInstance()
                    .getSharedPreferences("ecobridge_prefs", android.content.Context.MODE_PRIVATE);
            if (url == null || url.trim().isEmpty()) {
                prefs.edit().remove("pref_server_url").apply();
            } else {
                prefs.edit().putString("pref_server_url", url.trim()).apply();
            }
            retrofit = null;
            cachedBaseUrl = null;
        } catch (Throwable ignored) {}
    }

    public static ApiService getApiService() {
        return getClient(getBaseUrl()).create(ApiService.class);
    }

    public static synchronized Retrofit getClient(String baseUrl) {
        String normalizedUrl = baseUrl.replaceAll("/api/v1/?$", "");
        if (!normalizedUrl.endsWith("/")) {
            normalizedUrl += "/";
        }

        if (retrofit == null || !normalizedUrl.equals(cachedBaseUrl)) {
            cachedBaseUrl = normalizedUrl;
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
                    .baseUrl(normalizedUrl)
                    .client(client)
                    .addConverterFactory(GsonConverterFactory.create())
                    .build();
        }
        return retrofit;
    }
}
