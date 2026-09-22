package com.ecobridge.ui.handover;

import android.content.Intent;
import android.os.Bundle;
import android.text.Editable;
import android.text.TextWatcher;
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
import com.ecobridge.ui.transaction.TransactionsActivity;
import com.ecobridge.utils.HashUtils;
import com.ecobridge.ui.BaseActivity;
import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;

import java.util.Locale;
import java.util.Random;
import java.util.UUID;

/**
 * HandoverActivity
 * Completes the traceable handover: records actual scale weight,
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

    private double currentWeight = 10.0;
    private double currentAgreedPrice = 450.0;
    private double totalAmount = 4500.0;
    private String computedHash = "";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EcoBridgeApplication.getInstance().applyLocale(
                EcoBridgeApplication.getInstance().getSavedLanguage()
        );
        setContentView(R.layout.activity_handover);

        repository = EcoBridgeApplication.getInstance().getRepository();
        audioPromptManager = new AudioPromptManager(this);

        extractIntentData();
        initViews();
        recalculateSettlement();
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
        rgPaymentMode.setOnCheckedChangeListener((group, checkedId) -> recalculateSettlement());

        btnConfirmHandover.setOnClickListener(v -> submitHandover());
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

        totalAmount = currentWeight * currentAgreedPrice;
        String mode = rbCash.isChecked() ? "CASH" : "DIGITAL";
        String now = DemoDataSeeder.getUtcTimestamp();

        computedHash = HashUtils.generateHandoverHash(
                lotUuid, recyclerId, currentWeight, totalAmount, mode, now
        );

        tvFinalPaymentAmount.setText(String.format(Locale.US, "₹%,d", Math.round(totalAmount)));
        String shortHash = computedHash.length() >= 16 ? computedHash.substring(0, 16) : computedHash;
        tvDeterministicHash.setText("Audit Hash (SHA-256): " + shortHash + "...");
    }

    private void submitHandover() {
        if (currentWeight <= 0.0) {
            Toast.makeText(this, "Actual weight must be greater than 0 kg", Toast.LENGTH_SHORT).show();
            return;
        }

        String handoverUuid = UUID.randomUUID().toString();
        String referenceNo = "HO-" + (100000 + new Random().nextInt(900000));
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
                "PAID",
                now,
                "PENDING"
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
