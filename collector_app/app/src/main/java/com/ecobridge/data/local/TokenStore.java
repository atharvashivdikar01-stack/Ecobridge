package com.ecobridge.data.local;

import android.content.Context;
import androidx.security.crypto.EncryptedSharedPreferences;
import androidx.security.crypto.MasterKey;

/** Securely stores tokens outside the offline collection database. */
public final class TokenStore {
    private TokenStore() { }
    private static android.content.SharedPreferences preferences(Context context) {
        try {
            MasterKey key = new MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build();
            return EncryptedSharedPreferences.create(context, "ecobridge_auth", key,
                    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM);
        } catch (Exception error) { throw new IllegalStateException("Secure storage unavailable", error); }
    }
    public static String accessToken(Context context) { return preferences(context).getString("access", null); }
    public static boolean hasAccessToken(Context context) { return accessToken(context) != null; }
    public static void save(Context context, String access, String refresh) {
        preferences(context).edit().putString("access", access).putString("refresh", refresh).apply();
    }
}
