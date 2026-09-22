package com.ecobridge.ui.transaction;

import android.os.Bundle;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.R;
import com.ecobridge.data.local.entity.LotEntity;
import com.ecobridge.data.repository.EcoBridgeRepository;
import com.ecobridge.ui.BaseActivity;
import com.google.android.material.appbar.MaterialToolbar;

import java.util.Locale;

/**
 * TransactionDetailActivity
 * Shows detailed information about a specific transaction/lot.
 */
public class TransactionDetailActivity extends BaseActivity {

    private EcoBridgeRepository repository;
    private String lotUuid;

    private TextView tvLotCode;
    private TextView tvMaterial;
    private TextView tvWeight;
    private TextView tvCategory;
    private TextView tvEstimatedValue;
    private TextView tvNetEarnings;
    private TextView tvRecyclerName;
    private TextView tvStatus;
    private TextView tvSyncStatus;
    private TextView tvCreatedAt;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EcoBridgeApplication.getInstance().applyLocale(
                EcoBridgeApplication.getInstance().getSavedLanguage()
        );
        setContentView(R.layout.activity_transaction_detail);

        repository = EcoBridgeApplication.getInstance().getRepository();
        lotUuid = getIntent().getStringExtra("lot_uuid");

        initViews();
        loadTransactionDetails();
    }

    private void initViews() {
        MaterialToolbar toolbar = findViewById(R.id.toolbar);
        if (toolbar != null) {
            toolbar.setNavigationOnClickListener(v -> finish());
        }

        tvLotCode = findViewById(R.id.tvLotCode);
        tvMaterial = findViewById(R.id.tvMaterial);
        tvWeight = findViewById(R.id.tvWeight);
        tvCategory = findViewById(R.id.tvCategory);
        tvEstimatedValue = findViewById(R.id.tvEstimatedValue);
        tvNetEarnings = findViewById(R.id.tvNetEarnings);
        tvRecyclerName = findViewById(R.id.tvRecyclerName);
        tvStatus = findViewById(R.id.tvStatus);
        tvSyncStatus = findViewById(R.id.tvSyncStatus);
        tvCreatedAt = findViewById(R.id.tvCreatedAt);
    }

    private void loadTransactionDetails() {
        repository.getLotByUuid(lotUuid, lot -> {
            if (lot != null) {
                runOnUiThread(() -> {
                    tvLotCode.setText(lot.getShortCode());
                    tvMaterial.setText(lot.getCategory());
                    tvWeight.setText(String.format(Locale.US, "%.1f kg", lot.getApproxWeightKg()));
                    tvCategory.setText(lot.getCategory());
                    tvEstimatedValue.setText(String.format(Locale.US, "₹%,d", Math.round(lot.getEstimatedValue())));
                    tvNetEarnings.setText(String.format(Locale.US, "₹%,d", Math.round(lot.getNetEarnings())));
                    tvRecyclerName.setText(lot.getSelectedRecyclerName());
                    tvStatus.setText(lot.getStatus());
                    tvSyncStatus.setText(lot.getSyncStatus());
                    tvCreatedAt.setText(lot.getCreatedAt());
                });
            }
        });
    }
}
