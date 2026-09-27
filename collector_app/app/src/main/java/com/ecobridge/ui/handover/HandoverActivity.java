package com.ecobridge.ui.handover;

import android.content.Intent;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.View;
import android.widget.EditText;
import android.widget.RadioButton;
import android.widget.RadioGroup;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.R;
import com.ecobridge.audio.AudioPromptManager;
import com.ecobridge.data.local.entity.HandoverEntity;
import com.ecobridge.data.repository.DemoDataSeeder;
import com.ecobridge.data.repository.EcoBridgeRepository;
import com.ecobridge.ui.BaseActivity;
import com.ecobridge.ui.transaction.TransactionsActivity;
import com.ecobridge.utils.HashUtils;
import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.card.MaterialCardView;
import com.google.android.material.textfield.TextInputEditText;

import java.security.SecureRandom;
import java.util.Locale;
import java.util.UUID;

/**
 * HandoverActivity
 * Completes the traceable handover: records actual scale weight,
 * computes tax compliance (Fixed 5% GST with CGST 2.5% + SGST 2.5% for IT record maintenance),
 * provides cash denomination counting (e.g. 2 x 10 Rs, 4 x 100 Rs),
 * verifies payment settlement (Cash / Digital), generates a deterministic
 * tamper-evident record hash, and updates the local immutable ledger.
 */
public class HandoverActivity extends BaseActivity {

    private EcoBridgeRepository repository;
    private AudioPromptManager audioPromptManager;

    private String lotUuid;
    private String shortCode;
    private String recyclerName;
    private String recyclerId;

    private TextInputEditText etActualWeight;
    private TextInputEditText etAgreedPrice;
    private RadioGroup rgPaymentMode;
    private RadioButton rbCash;
    private TextView tvFinalPaymentAmount;
    private TextView tvDeterministicHash;
    private MaterialButton btnConfirmHandover;

    // Tax Views & Variables (Fixed 5% GST for Income Tax & GST compliance)
    private TextView tvTaxableGross;
    private TextView tvGstAmount;
    private TextView tvGstSplit;
    private TextView tvTaxInvoiceNo;

    private double currentWeight = 10.0;
    private double currentAgreedPrice = 450.0;
    private double grossAmount = 4500.0;
    private final double taxRate = 5.0; // Fixed 5% GST for scrap e-waste (HSN 8548/8549)
    private double taxAmount = 225.0;
    private double cgstAmount = 112.5;
    private double sgstAmount = 112.5;
    private double totalAmount = 4725.0;
    private String taxInvoiceNo = "";
    private String computedHash = "";

    // Cash Denominations (Full Indian denominations with stepper +/- and direct text input)
    private MaterialCardView cardCashDenominations;
    private MaterialButton btnAutoFillNotes;
    private MaterialButton btnResetNotes;
    private TextView tvTotalCashCounted;
    private TextView tvCashMatchStatus;
    private TextView tvNotesBreakdownSummary;

    private static final int[] DENOM_VALUES = {500, 200, 100, 50, 20, 10, 5, 1};
    private final int[] noteCounts = new int[8];
    private final EditText[] countEditTexts = new EditText[8];
    private final TextView[] subtotalTextViews = new TextView[8];
    private String notesBreakdown = "No cash notes counted";
    private boolean isUpdatingNoteCounts = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EcoBridgeApplication.getInstance().applyLocale(
                EcoBridgeApplication.getInstance().getSavedLanguage()
        );
        setContentView(R.layout.activity_handover);

        repository = EcoBridgeApplication.getInstance().getRepository();
        audioPromptManager = new AudioPromptManager(this);

        // Generate a standard Income Tax & GST invoice number for audit trail
        taxInvoiceNo = "TXI-2026-MH-" + (100000 + new SecureRandom().nextInt(900000));

        extractIntentData();
        initViews();
        setupCashDenominationCounter();
        recalculateSettlement();

        audioPromptManager.playPrompt("start_handover", "Enter the final weight and confirm the payment amount.");
    }

    private void extractIntentData() {
        Intent intent = getIntent();
        lotUuid = intent.getStringExtra("lot_uuid");
        shortCode = intent.getStringExtra("short_code");
        recyclerName = intent.getStringExtra("recycler_name");
        recyclerId = intent.getStringExtra("recycler_id");
        currentWeight = intent.getDoubleExtra("weight", 10.0);

        if (lotUuid == null) lotUuid = UUID.randomUUID().toString();
        if (shortCode == null) shortCode = "LOT-DEMO1";
        if (recyclerName == null) recyclerName = "EcoRecycle India Pvt Ltd";
        if (recyclerId == null) recyclerId = "rec-001";
    }

    private void initViews() {
        MaterialToolbar toolbar = findViewById(R.id.toolbar);
        toolbar.setNavigationOnClickListener(v -> finish());

        TextView tvHandoverLotCode = findViewById(R.id.tvHandoverLotCode);
        TextView tvHandoverRecycler = findViewById(R.id.tvHandoverRecycler);

        tvHandoverLotCode.setText("LOT: " + shortCode);
        tvHandoverRecycler.setText("Recycler: " + recyclerName);

        etActualWeight = findViewById(R.id.etActualWeight);
        etAgreedPrice = findViewById(R.id.etAgreedPrice);
        rgPaymentMode = findViewById(R.id.rgPaymentMode);
        rbCash = findViewById(R.id.rbCash);
        tvFinalPaymentAmount = findViewById(R.id.tvFinalPaymentAmount);
        tvDeterministicHash = findViewById(R.id.tvDeterministicHash);
        btnConfirmHandover = findViewById(R.id.btnConfirmHandover);

        // Tax Views
        tvTaxableGross = findViewById(R.id.tvTaxableGross);
        tvGstAmount = findViewById(R.id.tvGstAmount);
        tvGstSplit = findViewById(R.id.tvGstSplit);
        tvTaxInvoiceNo = findViewById(R.id.tvTaxInvoiceNo);
        tvTaxInvoiceNo.setText(taxInvoiceNo);

        // Cash Denominations Container
        cardCashDenominations = findViewById(R.id.cardCashDenominations);
        btnAutoFillNotes = findViewById(R.id.btnAutoFillNotes);
        btnResetNotes = findViewById(R.id.btnResetNotes);
        tvTotalCashCounted = findViewById(R.id.tvTotalCashCounted);
        tvCashMatchStatus = findViewById(R.id.tvCashMatchStatus);
        tvNotesBreakdownSummary = findViewById(R.id.tvNotesBreakdownSummary);

        etActualWeight.setText(String.format(Locale.US, "%.1f", currentWeight));
        etAgreedPrice.setText(String.format(Locale.US, "%.1f", currentAgreedPrice));

        TextWatcher textWatcher = new TextWatcher() {
            @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            @Override public void onTextChanged(CharSequence s, int start, int count, int after) {
                recalculateSettlement();
            }
            @Override public void afterTextChanged(Editable s) {}
        };

        etActualWeight.addTextChangedListener(textWatcher);
        etAgreedPrice.addTextChangedListener(textWatcher);

        rgPaymentMode.setOnCheckedChangeListener((group, checkedId) -> {
            boolean isCash = rbCash.isChecked();
            cardCashDenominations.setVisibility(isCash ? View.VISIBLE : View.GONE);
            recalculateSettlement();
        });

        btnConfirmHandover.setOnClickListener(v -> submitHandover());
    }

    private void setupCashDenominationCounter() {
        int[] minusButtonIds = {
                R.id.btnMinus500, R.id.btnMinus200, R.id.btnMinus100, R.id.btnMinus50,
                R.id.btnMinus20, R.id.btnMinus10, R.id.btnMinus5, R.id.btnMinusCoins
        };
        int[] plusButtonIds = {
                R.id.btnPlus500, R.id.btnPlus200, R.id.btnPlus100, R.id.btnPlus50,
                R.id.btnPlus20, R.id.btnPlus10, R.id.btnPlus5, R.id.btnPlusCoins
        };
        int[] countEditTextIds = {
                R.id.etCount500, R.id.etCount200, R.id.etCount100, R.id.etCount50,
                R.id.etCount20, R.id.etCount10, R.id.etCount5, R.id.etCountCoins
        };
        int[] subtotalTextViewIds = {
                R.id.tvSubtotal500, R.id.tvSubtotal200, R.id.tvSubtotal100, R.id.tvSubtotal50,
                R.id.tvSubtotal20, R.id.tvSubtotal10, R.id.tvSubtotal5, R.id.tvSubtotalCoins
        };

        for (int i = 0; i < 8; i++) {
            final int index = i;
            MaterialButton btnMinus = findViewById(minusButtonIds[i]);
            MaterialButton btnPlus = findViewById(plusButtonIds[i]);
            countEditTexts[i] = findViewById(countEditTextIds[i]);
            subtotalTextViews[i] = findViewById(subtotalTextViewIds[i]);

            btnPlus.setOnClickListener(v -> {
                noteCounts[index]++;
                updateDenominationRowUI(index);
                updateCashCountSummary();
            });

            btnMinus.setOnClickListener(v -> {
                if (noteCounts[index] > 0) {
                    noteCounts[index]--;
                    updateDenominationRowUI(index);
                    updateCashCountSummary();
                }
            });

            countEditTexts[i].addTextChangedListener(new TextWatcher() {
                @Override public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
                @Override public void onTextChanged(CharSequence s, int start, int count, int after) {
                    if (isUpdatingNoteCounts) return;
                    try {
                        String str = s.toString().trim();
                        noteCounts[index] = str.isEmpty() ? 0 : Integer.parseInt(str);
                    } catch (NumberFormatException e) {
                        noteCounts[index] = 0;
                    }
                    int subtotal = noteCounts[index] * DENOM_VALUES[index];
                    subtotalTextViews[index].setText(String.format(Locale.US, "₹%,d", subtotal));
                    updateCashCountSummary();
                }
                @Override public void afterTextChanged(Editable s) {}
            });
        }

        // Auto-Fill exact change button using greedy change algorithm
        btnAutoFillNotes.setOnClickListener(v -> autoFillExactNotes());

        // Reset notes button
        btnResetNotes.setOnClickListener(v -> resetAllNotes());
    }

    private void updateDenominationRowUI(int index) {
        isUpdatingNoteCounts = true;
        countEditTexts[index].setText(String.valueOf(noteCounts[index]));
        int subtotal = noteCounts[index] * DENOM_VALUES[index];
        subtotalTextViews[index].setText(String.format(Locale.US, "₹%,d", subtotal));
        isUpdatingNoteCounts = false;
    }

    private void autoFillExactNotes() {
        long remaining = Math.round(totalAmount);
        isUpdatingNoteCounts = true;
        for (int i = 0; i < DENOM_VALUES.length; i++) {
            int val = DENOM_VALUES[i];
            int count = (int) (remaining / val);
            noteCounts[i] = count;
            remaining %= val;
            countEditTexts[i].setText(String.valueOf(count));
            subtotalTextViews[i].setText(String.format(Locale.US, "₹%,d", count * val));
        }
        isUpdatingNoteCounts = false;
        updateCashCountSummary();
    }

    private void resetAllNotes() {
        isUpdatingNoteCounts = true;
        for (int i = 0; i < DENOM_VALUES.length; i++) {
            noteCounts[i] = 0;
            countEditTexts[i].setText("0");
            subtotalTextViews[i].setText("₹0");
        }
        isUpdatingNoteCounts = false;
        updateCashCountSummary();
    }

    private void updateCashCountSummary() {
        int totalCounted = 0;
        int totalNotes = 0;
        StringBuilder sb = new StringBuilder();

        for (int i = 0; i < DENOM_VALUES.length; i++) {
            int count = noteCounts[i];
            int val = DENOM_VALUES[i];
            totalCounted += count * val;
            totalNotes += count;

            if (count > 0) {
                if (sb.length() > 0) sb.append(", ");
                if (i == DENOM_VALUES.length - 1) {
                    sb.append(count).append(" × Coins");
                } else {
                    sb.append(count).append(" × ₹").append(val);
                }
            }
        }

        if (sb.length() == 0) {
            notesBreakdown = "No cash notes counted";
        } else {
            notesBreakdown = sb.toString() + " = ₹" + String.format(Locale.US, "%,d", totalCounted);
        }

        tvNotesBreakdownSummary.setText(notesBreakdown);
        tvTotalCashCounted.setText(getString(R.string.total_notes_count_summary,
                String.format(Locale.US, "%,d", totalCounted), totalNotes));

        long target = Math.round(totalAmount);
        if (totalCounted == target) {
            tvCashMatchStatus.setText(getString(R.string.cash_match_exact, String.format(Locale.US, "%,d", totalCounted)));
            tvCashMatchStatus.setBackgroundColor(getColor(R.color.primary_light));
            tvCashMatchStatus.setTextColor(getColor(R.color.status_online));
        } else if (totalCounted < target) {
            long diff = target - totalCounted;
            tvCashMatchStatus.setText(getString(R.string.cash_short, String.format(Locale.US, "%,d", diff)));
            tvCashMatchStatus.setBackgroundColor(getColor(R.color.surface_container_high));
            tvCashMatchStatus.setTextColor(getColor(R.color.secondary));
        } else {
            long excess = totalCounted - target;
            tvCashMatchStatus.setText(getString(R.string.cash_excess, String.format(Locale.US, "%,d", excess)));
            tvCashMatchStatus.setBackgroundColor(getColor(R.color.tertiary_fixed));
            tvCashMatchStatus.setTextColor(getColor(R.color.tertiary));
        }
    }

    private void recalculateSettlement() {
        try {
            String wtStr = etActualWeight.getText() != null ? etActualWeight.getText().toString() : "0";
            String prStr = etAgreedPrice.getText() != null ? etAgreedPrice.getText().toString() : "0";
            currentWeight = Double.parseDouble(wtStr);
            currentAgreedPrice = Double.parseDouble(prStr);
        } catch (NumberFormatException e) {
            currentWeight = 0.0;
            currentAgreedPrice = 0.0;
        }

        // Tax calculation: Fixed 5% GST for scrap e-waste (HSN 8548/8549)
        grossAmount = currentWeight * currentAgreedPrice;
        cgstAmount = Math.round(grossAmount * 0.025 * 100.0) / 100.0;
        sgstAmount = Math.round(grossAmount * 0.025 * 100.0) / 100.0;
        taxAmount = cgstAmount + sgstAmount;
        totalAmount = grossAmount + taxAmount;

        String mode = rbCash.isChecked() ? "CASH" : "DIGITAL";
        String now = DemoDataSeeder.getUtcTimestamp();

        computedHash = HashUtils.generateHandoverHash(
                lotUuid, recyclerId, currentWeight, grossAmount, taxAmount, totalAmount, taxInvoiceNo, mode, now
        );

        // Update Tax Views
        tvTaxableGross.setText(String.format(Locale.US, "₹%,.2f", grossAmount));
        tvGstAmount.setText(String.format(Locale.US, "+₹%,.2f", taxAmount));
        tvGstSplit.setText(String.format(Locale.US, "CGST 2.5%% (₹%.2f) + SGST 2.5%% (₹%.2f)", cgstAmount, sgstAmount));

        // Update Final Settlement Total
        tvFinalPaymentAmount.setText(String.format(Locale.US, "₹%,d", Math.round(totalAmount)));
        String shortHash = computedHash.length() >= 16 ? computedHash.substring(0, 16) : computedHash;
        tvDeterministicHash.setText("Audit Hash (SHA-256): " + shortHash + "...");

        // Update Cash summary comparison with the new totalAmount
        updateCashCountSummary();
    }

    private void submitHandover() {
        if (currentWeight <= 0.0) {
            Toast.makeText(this, "Actual weight must be greater than 0 kg", Toast.LENGTH_SHORT).show();
            return;
        }

        String handoverUuid = UUID.randomUUID().toString();
        String referenceNo = "HO-" + (100000 + new SecureRandom().nextInt(900000));
        String mode = rbCash.isChecked() ? "CASH" : "DIGITAL";
        String now = DemoDataSeeder.getUtcTimestamp();

        HandoverEntity handover = new HandoverEntity(
                handoverUuid,
                referenceNo,
                lotUuid,
                recyclerId,
                recyclerName,
                currentWeight,
                currentAgreedPrice,
                computedHash,
                mode,
                totalAmount,
                "PENDING_CONFIRMATION",
                now,
                "PENDING",
                grossAmount,
                taxRate,
                taxAmount,
                cgstAmount,
                sgstAmount,
                taxInvoiceNo,
                mode.equals("CASH") ? notesBreakdown : "DIGITAL_SETTLEMENT"
        );

        repository.createHandover(handover, new EcoBridgeRepository.OnHandoverCreatedCallback() {
            @Override
            public void onSuccess(HandoverEntity createdHandover) {
                audioPromptManager.playPrompt("handover_confirmed", getString(R.string.handover_success));
                Toast.makeText(HandoverActivity.this, R.string.handover_success, Toast.LENGTH_LONG).show();

                // Open Transactions Ledger
                Intent intent = new Intent(HandoverActivity.this, TransactionsActivity.class);
                intent.addFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP);
                startActivity(intent);
                finish();
            }

            @Override
            public void onError(Exception e) {
                Toast.makeText(HandoverActivity.this, "Error recording handover: " + e.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (audioPromptManager != null) {
            audioPromptManager.release();
        }
    }
}
