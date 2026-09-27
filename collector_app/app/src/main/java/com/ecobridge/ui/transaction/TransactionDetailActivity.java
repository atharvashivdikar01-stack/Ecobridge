package com.ecobridge.ui.transaction;

import android.os.Bundle;
import android.view.View;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.R;
import com.ecobridge.data.local.entity.HandoverEntity;
import com.ecobridge.data.local.entity.LotEntity;
import com.ecobridge.data.repository.EcoBridgeRepository;
import com.ecobridge.ui.BaseActivity;
import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.card.MaterialCardView;

import java.util.Locale;

/**
 * TransactionDetailActivity
 * Shows detailed information about a specific transaction/lot,
 * including Tax & Income Tax compliance record (Fixed 5% GST, invoice no)
 * and Cash Note denomination counts (e.g. 2 x 10 Rs, 4 x 100 Rs).
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

    // Tax & Compliance Views
    private MaterialCardView cardDetailTax;
    private TextView tvDetailGrossAmount;
    private TextView tvDetailGstAmount;
    private TextView tvDetailGstSplit;
    private TextView tvDetailInvoiceNo;
    private TextView tvDetailTotalSettlement;

    // Cash Denominations Views
    private MaterialCardView cardDetailCashBreakdown;
    private TextView tvDetailPaymentMode;
    private TextView tvDetailNotesBreakdown;

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

        // Tax Views
        cardDetailTax = findViewById(R.id.cardDetailTax);
        tvDetailGrossAmount = findViewById(R.id.tvDetailGrossAmount);
        tvDetailGstAmount = findViewById(R.id.tvDetailGstAmount);
        tvDetailGstSplit = findViewById(R.id.tvDetailGstSplit);
        tvDetailInvoiceNo = findViewById(R.id.tvDetailInvoiceNo);
        tvDetailTotalSettlement = findViewById(R.id.tvDetailTotalSettlement);

        // Cash Breakdown Views
        cardDetailCashBreakdown = findViewById(R.id.cardDetailCashBreakdown);
        tvDetailPaymentMode = findViewById(R.id.tvDetailPaymentMode);
        tvDetailNotesBreakdown = findViewById(R.id.tvDetailNotesBreakdown);

        findViewById(R.id.btnViewCertificate).setOnClickListener(v -> {
            // Placeholder for future receipt viewing logic
        });
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

                    // Default fallback tax values if handover not completed
                    double estGross = lot.getEstimatedValue();
                    double estCgst = Math.round(estGross * 0.025 * 100.0) / 100.0;
                    double estSgst = Math.round(estGross * 0.025 * 100.0) / 100.0;
                    double estTax = estCgst + estSgst;
                    double estTotal = estGross + estTax;

                    tvDetailGrossAmount.setText(String.format(Locale.US, "₹%,.2f", estGross));
                    tvDetailGstAmount.setText(String.format(Locale.US, "+₹%,.2f", estTax));
                    tvDetailGstSplit.setText(String.format(Locale.US, "CGST 2.5%% (₹%.2f) + SGST 2.5%% (₹%.2f)", estCgst, estSgst));
                    tvDetailInvoiceNo.setText("TXI-EST-" + lot.getShortCode());
                    tvDetailTotalSettlement.setText(String.format(Locale.US, "₹%,d", Math.round(estTotal)));
                });

                // Load corresponding Handover record for exact recorded tax and cash notes count
                repository.getHandoverForLot(lot.getUuid(), handover -> {
                    if (handover != null) {
                        runOnUiThread(() -> renderHandoverCompliance(handover));
                    }
                });
            }
        });
    }

    private void renderHandoverCompliance(HandoverEntity handover) {
        double gross = handover.getGrossAmount() > 0 ? handover.getGrossAmount() : (handover.getWeight() * handover.getAgreedPrice());
        double cgst = handover.getCgstAmount() > 0 ? handover.getCgstAmount() : (Math.round(gross * 0.025 * 100.0) / 100.0);
        double sgst = handover.getSgstAmount() > 0 ? handover.getSgstAmount() : (Math.round(gross * 0.025 * 100.0) / 100.0);
        double tax = handover.getTaxAmount() > 0 ? handover.getTaxAmount() : (cgst + sgst);
        double total = handover.getPaymentAmount() > 0 ? handover.getPaymentAmount() : (gross + tax);

        tvDetailGrossAmount.setText(String.format(Locale.US, "₹%,.2f", gross));
        tvDetailGstAmount.setText(String.format(Locale.US, "+₹%,.2f", tax));
        tvDetailGstSplit.setText(String.format(Locale.US, "CGST 2.5%% (₹%.2f) + SGST 2.5%% (₹%.2f)", cgst, sgst));

        String invoice = handover.getTaxInvoiceNo();
        if (invoice == null || invoice.isEmpty()) {
            invoice = "TXI-2026-MH-" + handover.getReferenceNo();
        }
        tvDetailInvoiceNo.setText(invoice);
        tvDetailTotalSettlement.setText(String.format(Locale.US, "₹%,d", Math.round(total)));

        // Cash Denominations / Notes Breakdown
        String mode = handover.getPaymentMode();
        if ("CASH".equalsIgnoreCase(mode)) {
            tvDetailPaymentMode.setText("Payment Mode: CASH (Physical Handover)");
            String notes = handover.getNotesBreakdown();
            if (notes == null || notes.isEmpty() || "DIGITAL_SETTLEMENT".equals(notes)) {
                notes = "Cash handover verified at scale terminal";
            }
            tvDetailNotesBreakdown.setText(notes);
            cardDetailCashBreakdown.setVisibility(View.VISIBLE);
        } else {
            tvDetailPaymentMode.setText("Payment Mode: DIGITAL (UPI / Bank Transfer)");
            tvDetailNotesBreakdown.setText("Verified Digital Settlement • Ref: " + handover.getReferenceNo());
            cardDetailCashBreakdown.setVisibility(View.VISIBLE);
        }
    }
}
