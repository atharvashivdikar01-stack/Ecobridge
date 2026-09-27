package com.ecobridge.ui.lot;

import android.content.Intent;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.R;
import com.ecobridge.ui.handover.HandoverActivity;
import com.ecobridge.ui.home.HomeActivity;
import com.ecobridge.utils.QrUtils;
import com.ecobridge.ui.BaseActivity;
import com.google.android.material.button.MaterialButton;

import java.util.Locale;

/**
 * LotCreatedActivity
 * Displays confirmation of newly created lot, generated lot short code,
 * summary metrics, and offline QR Code for recycler gate inwarding.
 */
public class LotCreatedActivity extends BaseActivity {

    private String lotUuid;
    private String shortCode;
    private String category;
    private double weight;
    private double estimatedValue;
    private double netEarnings;
    private String recyclerName;
    private String recyclerId;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EcoBridgeApplication.getInstance().applyLocale(
                EcoBridgeApplication.getInstance().getSavedLanguage()
        );
        setContentView(R.layout.activity_lot_created);

        extractIntentData();
        initViews();
    }

    private void extractIntentData() {
        Intent intent = getIntent();
        lotUuid = intent.getStringExtra("lot_uuid");
        shortCode = intent.getStringExtra("short_code");
        category = intent.getStringExtra("category");
        weight = intent.getDoubleExtra("weight", 10.0);
        estimatedValue = intent.getDoubleExtra("estimated_value", 4500.0);
        netEarnings = intent.getDoubleExtra("net_earnings", 4100.0);
        recyclerName = intent.getStringExtra("recycler_name");
        recyclerId = intent.getStringExtra("recycler_id");

        if (shortCode == null) shortCode = "LOT-DEMO1";
        if (category == null) category = "Copper";
        if (recyclerName == null) recyclerName = "EcoRecycle India";
    }

    private void initViews() {
        TextView tvLotCode = findViewById(R.id.tvLotCode);
        TextView tvQrContent = findViewById(R.id.tvQrContent);
        ImageView ivQrCode = findViewById(R.id.ivQrCode);
        TextView tvSummaryMaterialWeight = findViewById(R.id.tvSummaryMaterialWeight);
        TextView tvSummaryRecycler = findViewById(R.id.tvSummaryRecycler);
        TextView tvSummaryNetEarnings = findViewById(R.id.tvSummaryNetEarnings);

        tvLotCode.setText(shortCode);
        tvQrContent.setText("ECOBRIDGE:" + shortCode);
        tvSummaryMaterialWeight.setText(String.format(Locale.US, "%s • %.1f KG", category, weight));
        tvSummaryRecycler.setText(recyclerName);
        tvSummaryNetEarnings.setText(String.format(Locale.US, "₹%,d", Math.round(netEarnings)));

        // Generate QR Code bitmap offline using ZXing
        Bitmap qrBitmap = QrUtils.generateLotQr(shortCode, 450);
        if (qrBitmap != null) {
            ivQrCode.setImageBitmap(qrBitmap);
        }

        // Proceed to Handover
        MaterialButton btnProceedHandover = findViewById(R.id.btnProceedHandover);
        btnProceedHandover.setOnClickListener(v -> {
            Intent intent = new Intent(LotCreatedActivity.this, HandoverActivity.class);
            intent.putExtra("lot_uuid", lotUuid);
            intent.putExtra("short_code", shortCode);
            intent.putExtra("category", category);
            intent.putExtra("weight", weight);
            intent.putExtra("recycler_name", recyclerName);
            intent.putExtra("recycler_id", recyclerId);
            startActivity(intent);
            finish();
        });

        // Save & Return Home
        MaterialButton btnSaveAndHome = findViewById(R.id.btnSaveAndHome);
        btnSaveAndHome.setOnClickListener(v -> {
            Intent intent = new Intent(LotCreatedActivity.this, HomeActivity.class);
            intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(intent);
            finish();
        });
    }
}
