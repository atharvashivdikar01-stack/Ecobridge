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

    private TextView tvConnectionStatus;
    private TextView tvSyncDetails;
    private ImageView ivStatusIcon;
    private MaterialButton btnLanguage;
    private MaterialButton btnQuickSync;

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
        observeSyncStatus();
        setupClickListeners();
    }

    @Override
    protected void onResume() {
        super.onResume();
        setupLanguageDisplay();
        updateNetworkDisplay(0);
    }

    private void initViews() {
        tvConnectionStatus = findViewById(R.id.tvConnectionStatus);
        tvSyncDetails = findViewById(R.id.tvSyncDetails);
        ivStatusIcon = findViewById(R.id.ivStatusIcon);
        btnLanguage = findViewById(R.id.btnLanguage);
        btnQuickSync = findViewById(R.id.btnQuickSync);
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

    private void observeSyncStatus() {
        repository.getPendingSyncCount().observe(this, count -> {
            int pending = count != null ? count : 0;
            updateNetworkDisplay(pending);
        });
    }

    private void updateNetworkDisplay(int pendingCount) {
        boolean isConnected = NetworkUtils.isNetworkAvailable(this);

        if (isConnected) {
            tvConnectionStatus.setText(R.string.status_online);
            tvConnectionStatus.setTextColor(getColor(R.color.status_online));
            ivStatusIcon.setImageResource(R.drawable.ic_check_circle);
            ivStatusIcon.setColorFilter(getColor(R.color.status_online));

            if (pendingCount > 0) {
                tvSyncDetails.setText(getString(R.string.sync_pending_count, pendingCount));
                btnQuickSync.setVisibility(View.VISIBLE);
            } else {
                tvSyncDetails.setText(R.string.sync_all_synced);
                btnQuickSync.setVisibility(View.GONE);
            }
        } else {
            tvConnectionStatus.setText(R.string.status_offline);
            tvConnectionStatus.setTextColor(getColor(R.color.status_offline));
            ivStatusIcon.setImageResource(R.drawable.ic_sync);
            ivStatusIcon.setColorFilter(getColor(R.color.status_offline));

            if (pendingCount > 0) {
                tvSyncDetails.setText(getString(R.string.sync_pending_count, pendingCount));
            } else {
                tvSyncDetails.setText("Working offline. Records saved to phone.");
            }
            btnQuickSync.setVisibility(View.GONE);
        }
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

        // 5. Sync
        View.OnClickListener syncAction = v -> {
            if (NetworkUtils.isNetworkAvailable(HomeActivity.this)) {
                SyncWorker.triggerImmediateSync(HomeActivity.this);
                Toast.makeText(HomeActivity.this, R.string.status_syncing, Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(HomeActivity.this, "Cannot sync: device is offline. Will sync when internet reconnects.", Toast.LENGTH_LONG).show();
            }
        };
        findViewById(R.id.cardSync).setOnClickListener(syncAction);
        btnQuickSync.setOnClickListener(syncAction);

        // 6. Help & Safety Guidance Dialog
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
