package com.ecobridge;

import android.app.Application;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.res.Configuration;
import android.content.res.Resources;
import android.util.Log;

import com.ecobridge.data.local.AppDatabase;
import com.ecobridge.data.repository.DemoDataSeeder;
import com.ecobridge.data.repository.EcoBridgeRepository;

import java.util.Locale;

/**
 * EcoBridgeApplication
 * Core application instance initializing local SQLite/Room database,
 * repository singletons, locale configurations, and demo seed data.
 */
public class EcoBridgeApplication extends Application {

    private static final String TAG = "EcoBridgeApp";
    private static final String PREF_NAME = "ecobridge_prefs";
    private static final String KEY_LANGUAGE = "pref_language";

    private static EcoBridgeApplication instance;
    private AppDatabase database;
    private EcoBridgeRepository repository;

    @Override
    protected void attachBaseContext(Context base) {
        // Apply locale before any resources are loaded
        String lang = getLanguageFromPrefs(base);
        super.attachBaseContext(wrapContext(base, lang));
    }

    @Override
    public void onCreate() {
        super.onCreate();
        instance = this;

        // Apply persisted language preference on application launch
        applyLocale(getSavedLanguage());

        // Initialize local Room database
        database = AppDatabase.getInstance(this);
        repository = new EcoBridgeRepository(database, this);

        // Populate initial benchmark prices and verified recyclers if database is fresh
        DemoDataSeeder.seedInitialDataIfEmpty(database);

        // Schedule periodic background sync with WorkManager
        com.ecobridge.sync.SyncWorker.schedulePeriodicSync(this);

        Log.i(TAG, "EcoBridge initialized successfully in offline-first mode.");
    }

    public static EcoBridgeApplication getInstance() {
        return instance;
    }

    public AppDatabase getDatabase() {
        return database;
    }

    public EcoBridgeRepository getRepository() {
        return repository;
    }

    /**
     * Get currently saved user language code ('mr', 'hi', or 'en'). Default is Marathi ('mr').
     */
    public String getSavedLanguage() {
        return getLanguageFromPrefs(this);
    }

    /**
     * Static helper to read language pref before Application.onCreate (for attachBaseContext).
     */
    private static String getLanguageFromPrefs(Context context) {
        try {
            SharedPreferences prefs = context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
            return prefs.getString(KEY_LANGUAGE, "mr");
        } catch (Exception e) {
            return "mr";
        }
    }

    /**
     * Save and apply language code ('mr', 'hi', or 'en').
     */
    public void setLanguage(String languageCode) {
        SharedPreferences prefs = getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE);
        prefs.edit().putString(KEY_LANGUAGE, languageCode).apply();
        applyLocale(languageCode);
    }

    /**
     * Updates configuration locale for vernacular presentation across Application & Activities.
     * Uses only the manual Configuration approach for consistent behavior across all API levels.
     */
    public void applyLocale(String languageCode) {
        if (languageCode == null || languageCode.isEmpty()) {
            languageCode = "mr";
        }
        Locale locale = new Locale(languageCode);
        Locale.setDefault(locale);

        Resources resources = getResources();
        Configuration config = new Configuration(resources.getConfiguration());
        config.setLocale(locale);
        resources.updateConfiguration(config, resources.getDisplayMetrics());

        // Also update the base context configuration
        getBaseContext().getResources().updateConfiguration(config,
                getBaseContext().getResources().getDisplayMetrics());
    }

    /**
     * Wraps context with updated locale configuration for activity attachBaseContext.
     */
    public static Context wrapContext(Context context, String languageCode) {
        if (languageCode == null || languageCode.isEmpty()) {
            languageCode = "mr";
        }
        Locale locale = new Locale(languageCode);
        Locale.setDefault(locale);

        Configuration config = new Configuration(context.getResources().getConfiguration());
        config.setLocale(locale);
        return context.createConfigurationContext(config);
    }

    @Override
    public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
        // Re-apply our saved locale when system config changes (e.g. rotation)
        applyLocale(getSavedLanguage());
    }
}
