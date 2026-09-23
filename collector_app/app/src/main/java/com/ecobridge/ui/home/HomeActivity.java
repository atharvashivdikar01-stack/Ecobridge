package com.ecobridge.ui.home;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;

import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.R;
import com.ecobridge.audio.AudioPromptManager;
import com.ecobridge.data.repository.EcoBridgeRepository;
import com.ecobridge.sync.SyncWorker;
import com.ecobridge.ui.BaseActivity;
import com.ecobridge.ui.earnings.EarningsActivity;
import com.ecobridge.ui.lot.NewLotActivity;
import com.ecobridge.ui.price.PriceBoardActivity;
import com.ecobridge.ui.settings.LanguageActivity;
import com.ecobridge.ui.transaction.TransactionsActivity;
import com.ecobridge.utils.NetworkUtils;
import com.google.android.material.button.MaterialButton;

/**
 * HomeActivity
 * Primary dashboard for informal collectors. Designed for low literacy with large
 * touch targets, clear status indicators, and vernacular audio guidance.
 */
public class HomeActivity extends BaseActivity {

    private EcoBridgeRepository repository;
    private AudioPromptManager audioPromptManager;

    private MaterialButton btnLanguage;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EcoBridgeApplication.getInstance().applyLocale(
                EcoBridgeApplication.getInstance().getSavedLanguage()
        );
        setContentView(R.layout.activity_home);

        repository = EcoBridgeApplication.getInstance().getRepository();
        audioPromptManager = new AudioPromptManager(this);

        initViews();
        setupLanguageDisplay();
        setupClickListeners();
    }

    @Override
    protected void onResume() {
        super.onResume();
        setupLanguageDisplay();
    }

    private void initViews() {
        btnLanguage = findViewById(R.id.btnLanguage);
    }

    private void setupLanguageDisplay() {
        String lang = EcoBridgeApplication.getInstance().getSavedLanguage();
        if ("mr".equals(lang)) {
            btnLanguage.setText("मराठी");
        } else if ("hi".equals(lang)) {
            btnLanguage.setText("हिंदी");
        } else {
            btnLanguage.setText("English");
        }

        btnLanguage.setOnClickListener(v -> {
            Intent intent = new Intent(HomeActivity.this, LanguageActivity.class);
            startActivity(intent);
        });
    }

    private void setupClickListeners() {
        // 1. New Lot Action
        findViewById(R.id.cardNewLot).setOnClickListener(v -> {
            Intent intent = new Intent(HomeActivity.this, NewLotActivity.class);
            startActivity(intent);
        });

        // 2. Transactions
        findViewById(R.id.cardTransactions).setOnClickListener(v -> {
            Intent intent = new Intent(HomeActivity.this, TransactionsActivity.class);
            startActivity(intent);
        });

        // 3. Today's Prices
        findViewById(R.id.cardPrices).setOnClickListener(v -> {
            Intent intent = new Intent(HomeActivity.this, PriceBoardActivity.class);
            startActivity(intent);
        });

        // 4. My Earnings
        findViewById(R.id.cardEarnings).setOnClickListener(v -> {
            Intent intent = new Intent(HomeActivity.this, EarningsActivity.class);
            startActivity(intent);
        });

        // 5. Help & Safety Guidance Dialog
        findViewById(R.id.cardHelp).setOnClickListener(v -> showSafetyHelpDialog());
    }

    private void showSafetyHelpDialog() {
        new AlertDialog.Builder(this)
                .setTitle(R.string.action_help)
                .setMessage(
                        "🌿 ECOBRIDGE SAFETY RULES:\n\n" +
                        "1. ⚠️ BATTERY SAFETY: Never puncture, burn, or open swollen batteries. Keep away from water and heat.\n\n" +
                        "2. ⚠️ CRT GLASS: Contains hazardous lead. Do not break tubes. Use heavy gloves.\n\n" +
                        "3. 🤝 CASH PAYMENT: Always collect full agreed cash payment before final handover departure.\n\n" +
                        "4. 📱 OFFLINE USE: You can create scrap lots anywhere without internet. They sync automatically when you reconnect."
                )
                .setPositiveButton(R.string.btn_done, (dialog, which) -> dialog.dismiss())
                .show();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (audioPromptManager != null) {
            audioPromptManager.release();
        }
    }
}
