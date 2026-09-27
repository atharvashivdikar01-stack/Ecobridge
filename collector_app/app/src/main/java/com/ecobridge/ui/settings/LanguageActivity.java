package com.ecobridge.ui.settings;

import android.content.Intent;
import android.os.Bundle;
import android.widget.ImageView;

import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.R;
import com.ecobridge.ui.BaseActivity;
import com.ecobridge.ui.home.HomeActivity;
import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.card.MaterialCardView;

/**
 * LanguageActivity
 * Vernacular language selection (Marathi / Hindi / English).
 * On selection, restarts the entire activity stack so all UI updates.
 */
public class LanguageActivity extends BaseActivity {

    private ImageView ivCheckMarathi;
    private ImageView ivCheckHindi;
    private ImageView ivCheckEnglish;

    private MaterialCardView cardMarathi;
    private MaterialCardView cardHindi;
    private MaterialCardView cardEnglish;
    private String initialLanguage;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_language);

        initialLanguage = EcoBridgeApplication.getInstance().getSavedLanguage();

        MaterialToolbar toolbar = findViewById(R.id.toolbar);
        toolbar.setNavigationOnClickListener(v -> handleBack());

        ivCheckMarathi = findViewById(R.id.ivCheckMarathi);
        ivCheckHindi = findViewById(R.id.ivCheckHindi);
        ivCheckEnglish = findViewById(R.id.ivCheckEnglish);

        cardMarathi = findViewById(R.id.cardMarathi);
        cardHindi = findViewById(R.id.cardHindi);
        cardEnglish = findViewById(R.id.cardEnglish);

        highlightCurrentSelection();

        cardMarathi.setOnClickListener(v -> selectLanguage("mr"));
        cardHindi.setOnClickListener(v -> selectLanguage("hi"));
        cardEnglish.setOnClickListener(v -> selectLanguage("en"));

        findViewById(R.id.btnContinue).setOnClickListener(v -> {
            // Restart to apply language
            restartApp();
        });
    }

    private void highlightCurrentSelection() {
        String current = EcoBridgeApplication.getInstance().getSavedLanguage();
        int activeColor = getColor(R.color.primary);
        int inactiveColor = getColor(R.color.outline_variant);
        int vis_on = android.view.View.VISIBLE;
        int vis_off = android.view.View.INVISIBLE;

        ivCheckMarathi.setVisibility("mr".equals(current) ? vis_on : vis_off);
        ivCheckHindi.setVisibility("hi".equals(current) ? vis_on : vis_off);
        ivCheckEnglish.setVisibility("en".equals(current) ? vis_on : vis_off);

        ivCheckMarathi.setColorFilter(activeColor);
        ivCheckHindi.setColorFilter(activeColor);
        ivCheckEnglish.setColorFilter(activeColor);

        cardMarathi.setStrokeColor("mr".equals(current) ? activeColor : inactiveColor);
        cardHindi.setStrokeColor("hi".equals(current) ? activeColor : inactiveColor);
        cardEnglish.setStrokeColor("en".equals(current) ? activeColor : inactiveColor);
    }

    private void selectLanguage(String langCode) {
        EcoBridgeApplication app = EcoBridgeApplication.getInstance();
        app.setLanguage(langCode);

        // Update TTS language if audio manager is available
        if (audioManager != null) {
            audioManager.updateTtsLanguage();
        }

        highlightCurrentSelection();
    }

    @Override
    public void onBackPressed() {
        handleBack();
    }

    private void handleBack() {
        String current = EcoBridgeApplication.getInstance().getSavedLanguage();
        if (initialLanguage != null && !initialLanguage.equals(current)) {
            restartApp();
        } else {
            finish();
        }
    }

    private void restartApp() {
        // Clear entire task and restart from HomeActivity with new locale
        Intent intent = new Intent(this, HomeActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK | Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
        finishAffinity();
    }
}
