package com.ecobridge.ui.transaction;

import android.content.Intent;
import android.os.Bundle;
import android.widget.TextView;

import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.R;
import com.ecobridge.data.local.entity.LotEntity;
import com.ecobridge.data.repository.EcoBridgeRepository;
import com.ecobridge.ui.BaseActivity;
import com.ecobridge.ui.handover.HandoverActivity;
import com.google.android.material.appbar.MaterialToolbar;

import java.util.Locale;

/**
 * TransactionDetailActivity
 * Shows detailed information about a specific transaction/lot.
 */
public class TransactionDetailActivity extends BaseActivity {

    private EcoBridgeRepository repository;
    private LotEntity loadedLot;

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

        findViewById(R.id.btnViewCertificate).setOnClickListener(v -> {
            if (loadedLot == null) return;
            Intent intent = new Intent(this, HandoverActivity.class);
            intent.putExtra("lot_uuid", loadedLot.getUuid());
            intent.putExtra("short_code", loadedLot.getShortCode());
            intent.putExtra("recycler_name", loadedLot.getSelectedRecyclerName());
            intent.putExtra("recycler_id", loadedLot.getSelectedRecyclerId());
            intent.putExtra("weight", loadedLot.getApproxWeightKg());
            startActivity(intent);
        });
    }

    private void loadTransactionDetails() {
        repository.getLotByUuid(getIntent().getStringExtra("lot_uuid"), lot -> {
            if (lot != null) {
                loadedLot = lot;
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
