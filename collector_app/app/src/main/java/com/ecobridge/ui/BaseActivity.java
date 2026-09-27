package com.ecobridge.ui;

import android.content.Context;
import android.content.res.Configuration;
import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;

import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.audio.AudioPromptManager;

import java.util.Locale;

/**
 * BaseActivity
 * Base class for all activities providing unified locale configuration,
 * vernacular context wrapping, and shared utilities like AudioPromptManager.
 */
public abstract class BaseActivity extends AppCompatActivity {

    protected AudioPromptManager audioManager;

    @Override
    protected void attachBaseContext(Context newBase) {
        String lang = "mr";
        try {
            if (EcoBridgeApplication.getInstance() != null) {
                lang = EcoBridgeApplication.getInstance().getSavedLanguage();
            }
        } catch (Exception ignored) {}
        super.attachBaseContext(EcoBridgeApplication.wrapContext(newBase, lang));
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // Apply locale before super.onCreate to ensure correct resources
        applyActivityLocale();
        super.onCreate(savedInstanceState);
        audioManager = AudioPromptManager.getInstance(this);
    }

    @Override
    protected void onResume() {
        super.onResume();
        // Ensure locale is still correct after returning from another activity
        applyActivityLocale();
    }

    /**
     * Apply the saved locale to this activity's resources.
     */
    private void applyActivityLocale() {
        try {
            if (EcoBridgeApplication.getInstance() != null) {
                String lang = EcoBridgeApplication.getInstance().getSavedLanguage();
                Locale locale = new Locale(lang);
                Locale.setDefault(locale);
                Configuration config = new Configuration(getResources().getConfiguration());
                config.setLocale(locale);
                getResources().updateConfiguration(config, getResources().getDisplayMetrics());
            }
        } catch (Exception ignored) {}
    }

    @Override
    protected void onDestroy() {
        if (audioManager != null) {
            audioManager.release();
        }
        super.onDestroy();
    }
}
