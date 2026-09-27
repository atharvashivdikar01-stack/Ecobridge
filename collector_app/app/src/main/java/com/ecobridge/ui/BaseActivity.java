package com.ecobridge.ui;

import android.content.Context;
import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;

import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.audio.AudioPromptManager;

/**
 * BaseActivity
 * Base class for all activities providing unified locale configuration,
 * vernacular context wrapping, and shared utilities like AudioPromptManager.
 */
public abstract class BaseActivity extends AppCompatActivity {

    protected AudioPromptManager audioManager;

    @Override
    protected void attachBaseContext(Context newBase) {
        String lang = EcoBridgeApplication.getInstance() != null ?
                EcoBridgeApplication.getInstance().getSavedLanguage() : "mr";
        super.attachBaseContext(EcoBridgeApplication.wrapContext(newBase, lang));
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        if (EcoBridgeApplication.getInstance() != null) {
            EcoBridgeApplication.getInstance().applyLocale(
                    EcoBridgeApplication.getInstance().getSavedLanguage()
            );
        }
        super.onCreate(savedInstanceState);
        audioManager = new AudioPromptManager(this);
    }

    @Override
    protected void onDestroy() {
        if (audioManager != null) {
            audioManager.release();
        }
        super.onDestroy();
    }
}
