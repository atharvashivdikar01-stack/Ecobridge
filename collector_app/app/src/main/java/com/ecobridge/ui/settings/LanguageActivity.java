package com.ecobridge.ui.settings;

import android.content.Intent;
import android.os.Bundle;
import android.widget.ImageView;

import androidx.appcompat.app.AppCompatActivity;

import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.R;
import com.ecobridge.ui.BaseActivity;
import com.ecobridge.ui.home.HomeActivity;
import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.card.MaterialCardView;

/**
 * LanguageActivity
 * Vernacular language selection (Marathi / Hindi / English).
 */
public class LanguageActivity extends BaseActivity {

    private ImageView ivCheckMarathi;
    private ImageView ivCheckHindi;
    private ImageView ivCheckEnglish;

    private MaterialCardView cardMarathi;
    private MaterialCardView cardHindi;
    private MaterialCardView cardEnglish;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_language);

        MaterialToolbar toolbar = findViewById(R.id.toolbar);
        toolbar.setNavigationOnClickListener(v -> finish());

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
    }

    private void highlightCurrentSelection() {
        String current = EcoBridgeApplication.getInstance().getSavedLanguage();
        int activeColor = getColor(R.color.primary);
        int inactiveColor = getColor(R.color.text_hint);

        ivCheckMarathi.setColorFilter("mr".equals(current) ? activeColor : inactiveColor);
        ivCheckHindi.setColorFilter("hi".equals(current) ? activeColor : inactiveColor);
        ivCheckEnglish.setColorFilter("en".equals(current) ? activeColor : inactiveColor);

        cardMarathi.setStrokeColor("mr".equals(current) ? activeColor : getColor(R.color.card_stroke));
        cardHindi.setStrokeColor("hi".equals(current) ? activeColor : getColor(R.color.card_stroke));
        cardEnglish.setStrokeColor("en".equals(current) ? activeColor : getColor(R.color.card_stroke));
    }

    private void selectLanguage(String langCode) {
        EcoBridgeApplication.getInstance().setLanguage(langCode);
        highlightCurrentSelection();

        // Restart HomeActivity with updated locale configuration
        Intent intent = new Intent(this, HomeActivity.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(intent);
        finish();
    }
}
