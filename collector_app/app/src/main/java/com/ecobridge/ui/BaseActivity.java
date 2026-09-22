package com.ecobridge.ui;

import android.content.Context;
import android.os.Bundle;

import androidx.appcompat.app.AppCompatActivity;

import com.ecobridge.EcoBridgeApplication;

/**
 * BaseActivity
 * Base class for all activities providing unified locale configuration
 * and vernacular context wrapping.
 */
public abstract class BaseActivity extends AppCompatActivity {

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
    }
}
