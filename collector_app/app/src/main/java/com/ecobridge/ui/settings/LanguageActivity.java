package com.ecobridge.ui.settings;

import android.content.Intent;
import android.os.Bundle;
import android.widget.ImageView;
import android.widget.TextView;

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
    private MaterialCardView cardServerSettings;
    private TextView tvCurrentServerUrl;
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
        cardServerSettings = findViewById(R.id.cardServerSettings);
        tvCurrentServerUrl = findViewById(R.id.tvCurrentServerUrl);

        highlightCurrentSelection();
        updateServerUrlDisplay();

        cardMarathi.setOnClickListener(v -> selectLanguage("mr"));
        cardHindi.setOnClickListener(v -> selectLanguage("hi"));
        cardEnglish.setOnClickListener(v -> selectLanguage("en"));

        if (cardServerSettings != null) {
            cardServerSettings.setOnClickListener(v -> showServerConfigDialog());
        }

        findViewById(R.id.btnContinue).setOnClickListener(v -> {
            // Restart to apply language
            restartApp();
        });
    }

    private void updateServerUrlDisplay() {
        if (tvCurrentServerUrl != null) {
            String currentUrl = com.ecobridge.data.remote.RetrofitClient.getBaseUrl();
            tvCurrentServerUrl.setText(currentUrl);
        }
    }

    private void showServerConfigDialog() {
        String currentUrl = com.ecobridge.data.remote.RetrofitClient.getBaseUrl();

        android.widget.LinearLayout container = new android.widget.LinearLayout(this);
        container.setOrientation(android.widget.LinearLayout.VERTICAL);
        int pad = (int) (16 * getResources().getDisplayMetrics().density);
        container.setPadding(pad, pad, pad, pad);

        final android.widget.EditText input = new android.widget.EditText(this);
        input.setHint(R.string.server_url_hint);
        input.setText(currentUrl);
        input.setSingleLine(true);
        input.setInputType(android.text.InputType.TYPE_CLASS_TEXT | android.text.InputType.TYPE_TEXT_VARIATION_URI);
        container.addView(input);

        // Preset Quick Buttons
        android.widget.LinearLayout presets = new android.widget.LinearLayout(this);
        presets.setOrientation(android.widget.LinearLayout.HORIZONTAL);
        presets.setPadding(0, pad / 2, 0, 0);

        android.widget.Button btnEmu = new android.widget.Button(this, null, com.google.android.material.R.attr.materialButtonOutlinedStyle);
        btnEmu.setText(R.string.preset_emulator);
        btnEmu.setTextSize(11);
        btnEmu.setOnClickListener(v -> input.setText("http://10.0.2.2:8000/"));

        android.widget.Button btnCloud = new android.widget.Button(this, null, com.google.android.material.R.attr.materialButtonOutlinedStyle);
        btnCloud.setText(R.string.preset_render);
        btnCloud.setTextSize(11);
        btnCloud.setOnClickListener(v -> input.setText("https://ecobridge-api-sih26-d3hfbccrg3fpddcr.centralindia-01.azurewebsites.net/"));

        android.widget.LinearLayout.LayoutParams lp = new android.widget.LinearLayout.LayoutParams(0, android.widget.LinearLayout.LayoutParams.WRAP_CONTENT, 1f);
        lp.setMarginEnd(8);
        presets.addView(btnEmu, lp);
        presets.addView(btnCloud, new android.widget.LinearLayout.LayoutParams(0, android.widget.LinearLayout.LayoutParams.WRAP_CONTENT, 1f));
        container.addView(presets);

        new androidx.appcompat.app.AlertDialog.Builder(this)
                .setTitle(R.string.server_url_dialog_title)
                .setView(container)
                .setPositiveButton(R.string.btn_done, (dialog, which) -> {
                    String entered = input.getText().toString().trim();
                    if (!entered.isEmpty()) {
                        if (!entered.startsWith("http://") && !entered.startsWith("https://")) {
                            entered = "http://" + entered;
                        }
                        com.ecobridge.data.remote.RetrofitClient.setCustomBaseUrl(entered);
                        updateServerUrlDisplay();
                        android.widget.Toast.makeText(this, R.string.server_url_saved, android.widget.Toast.LENGTH_SHORT).show();
                    }
                })
                .setNeutralButton(R.string.btn_reset_default, (dialog, which) -> {
                    com.ecobridge.data.remote.RetrofitClient.setCustomBaseUrl(null);
                    updateServerUrlDisplay();
                    android.widget.Toast.makeText(this, R.string.server_url_saved, android.widget.Toast.LENGTH_SHORT).show();
                })
                .setNegativeButton(R.string.btn_cancel, (dialog, which) -> dialog.dismiss())
                .show();
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
