package com.ecobridge.ui;

import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;

import androidx.appcompat.app.AppCompatActivity;

import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.R;
import com.ecobridge.ui.home.HomeActivity;
import com.ecobridge.ui.auth.LoginActivity;

/**
 * MainActivity
 * Splash and routing entry point. Applies saved vernacular locale
 * and launches HomeActivity.
 */
public class MainActivity extends BaseActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EcoBridgeApplication.getInstance().applyLocale(
                EcoBridgeApplication.getInstance().getSavedLanguage()
        );
        setContentView(R.layout.activity_main);

        new Handler(Looper.getMainLooper()).postDelayed(() -> {
            Intent intent = new Intent(MainActivity.this,
                    com.ecobridge.data.local.TokenStore.hasAccessToken(MainActivity.this)
                            ? HomeActivity.class : LoginActivity.class);
            startActivity(intent);
            finish();
        }, 1000);
    }
}
