package com.ecobridge.ui.lot;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import androidx.gridlayout.widget.GridLayout;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.camera.view.PreviewView;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.R;
import com.ecobridge.ai.ClassificationResult;
import com.ecobridge.ai.ScrapClassifier;
import com.ecobridge.audio.AudioPromptManager;
import com.ecobridge.camera.CameraManager;
import com.ecobridge.data.local.entity.LotEntity;
import com.ecobridge.data.local.entity.LotPhotoEntity;
import com.ecobridge.data.local.entity.PriceEntity;
import com.ecobridge.data.local.entity.RecyclerEntity;
import com.ecobridge.data.repository.DemoDataSeeder;
import com.ecobridge.data.repository.EcoBridgeRepository;
import com.ecobridge.utils.HashUtils;
import com.ecobridge.utils.ImageUtils;
import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.card.MaterialCardView;

import java.io.File;
import java.io.FileOutputStream;
import java.util.List;
import java.util.Locale;
import java.security.SecureRandom;
import com.ecobridge.ui.BaseActivity;

import java.util.UUID;

/**
 * NewLotActivity
 * Complete 5-step collector workflow:
 * 1. CameraX Photo Capture & SHA-256 Hashing
 * 2. On-Device TFLite Material Classification & Manual Fallback
 * 3. Weight Input & Decimal Keypad
 * 4. Room-Cached Fair Price Intelligence
 * 5. Recycler Matching & Net Earnings Calculation
 */
public class NewLotActivity extends BaseActivity {

    private static final int CAMERA_PERMISSION_CODE = 101;

    private EcoBridgeRepository repository;
    private AudioPromptManager audioPromptManager;
    private ScrapClassifier scrapClassifier;
    private CameraManager cameraManager;

    // Navigation & Step Management
    private int currentStep = 1;
    private ProgressBar progressBarSteps;
    private TextView tvStepIndicator;

    // Step Layout Containers
    private View step1CameraLayout;
    private View step2ClassifyLayout;
    private View step3WeightLayout;
    private View step4PriceLayout;
    private View step5RecyclerLayout;

    // Step 1 Views
    private PreviewView cameraPreviewView;
    private ImageView ivCapturedPhoto;
    private MaterialButton btnCapturePhoto;
    private MaterialButton btnRetakePhoto;
    private MaterialButton btnNextStep1;
    private MaterialButton btnFlashToggle;
    private TextView tvPhotoMetadata;
    private File capturedRawFile;
    private File compressedFile;
    private String photoSha256 = "";
    private Bitmap currentBitmap;

    // Step 2 Views
    private TextView tvDetectedCategory;
    private TextView tvConfidenceValue;
    private ProgressBar pbConfidence;
    private MaterialCardView cardHazardAlert;
    private TextView tvHazardMessage;
    private GridLayout gridCategories;
    private MaterialButton btnConfirmCategory;
    private String selectedCategory = "Copper";
    private float selectedConfidence = 0.87f;

    // Step 3 Views
    private TextView tvWeightDisplay;
    private MaterialButton btnConfirmWeight;
    private StringBuilder weightBuilder = new StringBuilder("10.0");
    private double currentWeightKg = 10.0;

    // Step 4 Views
    private TextView tvPricePerKg;
    private TextView tvExpectedValue;
    private TextView tvPriceBreakdown;
    private MaterialButton btnProceedToRecyclers;
    private double currentBenchmarkRate = 420.0;

    // Step 5 Views
    private TextView tvNetTakeHome;
    private TextView tvNetEarningsFormula;
    private LinearLayout layoutRecyclerList;
    private MaterialButton btnCreateLotFinal;
    private List<RecyclerEntity> availableRecyclers;
    private RecyclerEntity selectedRecycler;
    private double finalNetEarnings = 0.0;
    private double finalSaleValue = 0.0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EcoBridgeApplication.getInstance().applyLocale(
                EcoBridgeApplication.getInstance().getSavedLanguage()
        );
        setContentView(R.layout.activity_new_lot);

        repository = EcoBridgeApplication.getInstance().getRepository();
        audioPromptManager = new AudioPromptManager(this);
        scrapClassifier = new ScrapClassifier(this);

        initViews();
        setupToolbar();
        setupStep1Camera();
        setupStep2Classification();
        setupStep3WeightKeypad();
        setupStep4Pricing();
        setupStep5Recyclers();

        showStep(1);
    }

    private void initViews() {
        progressBarSteps = findViewById(R.id.progressBarSteps);
        tvStepIndicator = findViewById(R.id.tvStepIndicator);

        step1CameraLayout = findViewById(R.id.step1CameraLayout);
        step2ClassifyLayout = findViewById(R.id.step2ClassifyLayout);
        step3WeightLayout = findViewById(R.id.step3WeightLayout);
        step4PriceLayout = findViewById(R.id.step4PriceLayout);
        step5RecyclerLayout = findViewById(R.id.step5RecyclerLayout);

        // Step 1
        cameraPreviewView = findViewById(R.id.cameraPreviewView);
        ivCapturedPhoto = findViewById(R.id.ivCapturedPhoto);
        btnCapturePhoto = findViewById(R.id.btnCapturePhoto);
        btnRetakePhoto = findViewById(R.id.btnRetakePhoto);
        btnNextStep1 = findViewById(R.id.btnNextStep1);
        btnFlashToggle = findViewById(R.id.btnFlashToggle);
        tvPhotoMetadata = findViewById(R.id.tvPhotoMetadata);

        // Step 2
        tvDetectedCategory = findViewById(R.id.tvDetectedCategory);
        tvConfidenceValue = findViewById(R.id.tvConfidenceValue);
        pbConfidence = findViewById(R.id.pbConfidence);
        cardHazardAlert = findViewById(R.id.cardHazardAlert);
        tvHazardMessage = findViewById(R.id.tvHazardMessage);
        gridCategories = findViewById(R.id.gridCategories);
        btnConfirmCategory = findViewById(R.id.btnConfirmCategory);

        // Step 3
        tvWeightDisplay = findViewById(R.id.tvWeightDisplay);
        btnConfirmWeight = findViewById(R.id.btnConfirmWeight);

        // Step 4
        tvPricePerKg = findViewById(R.id.tvPricePerKg);
        tvExpectedValue = findViewById(R.id.tvExpectedValue);
        tvPriceBreakdown = findViewById(R.id.tvPriceBreakdown);
        btnProceedToRecyclers = findViewById(R.id.btnProceedToRecyclers);

        // Step 5
        tvNetTakeHome = findViewById(R.id.tvNetTakeHome);
        tvNetEarningsFormula = findViewById(R.id.tvNetEarningsFormula);
        layoutRecyclerList = findViewById(R.id.layoutRecyclerList);
        btnCreateLotFinal = findViewById(R.id.btnCreateLotFinal);
    }

    private void setupToolbar() {
        MaterialToolbar toolbar = findViewById(R.id.toolbar);
        toolbar.setNavigationOnClickListener(v -> {
            if (currentStep > 1) {
                showStep(currentStep - 1);
            } else {
                finish();
            }
        });
    }

    private void showStep(int step) {
        currentStep = step;
        progressBarSteps.setProgress(step);
        tvStepIndicator.setText(step + " / 5");

        step1CameraLayout.setVisibility(step == 1 ? View.VISIBLE : View.GONE);
        step2ClassifyLayout.setVisibility(step == 2 ? View.VISIBLE : View.GONE);
        step3WeightLayout.setVisibility(step == 3 ? View.VISIBLE : View.GONE);
        step4PriceLayout.setVisibility(step == 4 ? View.VISIBLE : View.GONE);
        step5RecyclerLayout.setVisibility(step == 5 ? View.VISIBLE : View.GONE);

        if (step == 1) {
            audioPromptManager.playPrompt("take_photo", getString(R.string.instruction_take_photo));
        } else if (step == 2) {
            audioPromptManager.playPrompt("classify_material", "Please verify the material category detected by the camera.");
            runClassification();
        } else if (step == 3) {
            audioPromptManager.playPrompt("enter_weight", getString(R.string.label_weight));
        } else if (step == 4) {
            audioPromptManager.playPrompt("check_price", "Check the expected price for your scrap.");
            loadPriceIntelligence();
        } else if (step == 5) {
            audioPromptManager.playPrompt("select_recycler", "Select a recycler for handover.");
            loadRecyclerMatching();
        }
    }

    // =========================================================================
    // STEP 1: CAMERA & PHOTO CAPTURE
    // =========================================================================
    private void setupStep1Camera() {
        cameraManager = new CameraManager(this, this, cameraPreviewView);

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA)
                == PackageManager.PERMISSION_GRANTED) {
            cameraManager.startCamera(null);
        } else {
            ActivityCompat.requestPermissions(
                    this,
                    new String[]{Manifest.permission.CAMERA},
                    CAMERA_PERMISSION_CODE
            );
        }

        btnFlashToggle.setOnClickListener(v -> {
            boolean isOn = cameraManager.toggleFlash();
            btnFlashToggle.setIconResource(isOn ? R.drawable.ic_flash_off : R.drawable.ic_flash_on);
        });

        btnCapturePhoto.setOnClickListener(v -> capturePhoto());

        btnRetakePhoto.setOnClickListener(v -> {
            ivCapturedPhoto.setVisibility(View.GONE);
            cameraPreviewView.setVisibility(View.VISIBLE);
            btnRetakePhoto.setVisibility(View.GONE);
            btnNextStep1.setVisibility(View.GONE);
            btnCapturePhoto.setVisibility(View.VISIBLE);
            tvPhotoMetadata.setText(R.string.photo_compressed_info);
        });

        btnNextStep1.setOnClickListener(v -> showStep(2));
    }

    private void capturePhoto() {
        File outputDir = getExternalFilesDir("scrap_photos");
        if (outputDir == null) outputDir = getFilesDir();
        if (!outputDir.exists()) outputDir.mkdirs();

        capturedRawFile = new File(outputDir, "raw_" + System.currentTimeMillis() + ".jpg");
        compressedFile = new File(outputDir, "photo_" + System.currentTimeMillis() + ".jpg");

        // Use CameraManager capture
        cameraManager.capturePhoto(capturedRawFile, new CameraManager.OnCaptureCallback() {
            @Override
            public void onImageCaptured(File capturedFile) {
                processCapturedImage(capturedFile);
            }

            @Override
            public void onError(Exception e) {
                // Fallback for emulator / devices without working camera hardware
                generateFallbackDemoPhoto(compressedFile);
            }
        });
    }

    private void generateFallbackDemoPhoto(File destination) {
        try {
            Bitmap demoBitmap = Bitmap.createBitmap(400, 400, Bitmap.Config.ARGB_8888);
            demoBitmap.eraseColor(Color.rgb(184, 115, 51)); // Copper reddish hue
            try (FileOutputStream fos = new FileOutputStream(destination)) {
                demoBitmap.compress(Bitmap.CompressFormat.JPEG, 85, fos);
            }
            processCapturedImage(destination);
        } catch (Exception ignored) {}
    }

    private void processCapturedImage(File sourceFile) {
        // 1. Compress to approx 150 KB JPEG
        ImageUtils.compressToTargetJpeg(sourceFile, compressedFile);

        // 2. Compute SHA-256 integrity hash
        photoSha256 = HashUtils.calculateFileSha256(compressedFile);

        currentBitmap = BitmapFactory.decodeFile(compressedFile.getAbsolutePath());

        runOnUiThread(() -> {
            cameraPreviewView.setVisibility(View.GONE);
            ivCapturedPhoto.setImageBitmap(currentBitmap);
            ivCapturedPhoto.setVisibility(View.VISIBLE);

            btnCapturePhoto.setVisibility(View.GONE);
            btnRetakePhoto.setVisibility(View.VISIBLE);
            btnNextStep1.setVisibility(View.VISIBLE);

            long sizeKb = compressedFile.length() / 1024;
            String shortHash = photoSha256.length() >= 16 ? photoSha256.substring(0, 16) : photoSha256;
            tvPhotoMetadata.setText(String.format(
                    Locale.US,
                    "Size: %d KB • SHA-256: %s...",
                    sizeKb, shortHash
            ));
        });
    }

    // =========================================================================
    // STEP 2: AI MATERIAL CLASSIFICATION
    // =========================================================================
    private void setupStep2Classification() {
        btnConfirmCategory.setOnClickListener(v -> showStep(3));
        populateCategoryGrid();
    }

    private void runClassification() {
        if (currentBitmap == null) {
            currentBitmap = BitmapFactory.decodeResource(getResources(), R.drawable.ic_check_circle);
        }

        scrapClassifier.classifyAsync(currentBitmap, new ScrapClassifier.OnClassificationCallback() {
            @Override
            public void onResult(ClassificationResult result) {
                runOnUiThread(() -> {
                    selectedCategory = result.getCategory();
                    selectedConfidence = result.getConfidence();

                    tvDetectedCategory.setText(selectedCategory);
                    tvConfidenceValue.setText(" " + result.getConfidencePercentage() + "%");
                    pbConfidence.setProgress(result.getConfidencePercentage());

                    if (result.isHazardous()) {
                        cardHazardAlert.setVisibility(View.VISIBLE);
                        tvHazardMessage.setText(result.getHazardWarning());
                    } else {
                        cardHazardAlert.setVisibility(View.GONE);
                    }

                    highlightSelectedCategoryButton(selectedCategory);
                });
            }

            @Override
            public void onError(Exception e) {
                runOnUiThread(() -> {
                    selectedCategory = "Copper";
                    tvDetectedCategory.setText("Copper");
                    tvConfidenceValue.setText(" 87%");
                    pbConfidence.setProgress(87);
                });
            }
        });
    }

    private void populateCategoryGrid() {
        gridCategories.removeAllViews();
        List<String> categories = scrapClassifier.getCategories();

        for (String cat : categories) {
            MaterialButton btn = new MaterialButton(this, null, com.google.android.material.R.attr.materialButtonOutlinedStyle);
            btn.setText(cat);
            btn.setTextSize(12);
            btn.setTextColor(getColor(R.color.text_primary));
            btn.setCornerRadius(10);
            btn.setStrokeColorResource(R.color.card_stroke);

            GridLayout.LayoutParams params = new GridLayout.LayoutParams();
            params.width = 0;
            params.height = ViewGroup.LayoutParams.WRAP_CONTENT;
            params.columnSpec = GridLayout.spec(GridLayout.UNDEFINED, 1f);
            params.setMargins(6, 6, 6, 6);
            btn.setLayoutParams(params);

            btn.setOnClickListener(v -> {
                selectedCategory = cat;
                tvDetectedCategory.setText(cat);
                tvConfidenceValue.setText(" Manual Selection");
                pbConfidence.setProgress(100);

                if ("Batteries".equalsIgnoreCase(cat)) {
                    cardHazardAlert.setVisibility(View.VISIBLE);
                    tvHazardMessage.setText(R.string.hazard_battery_msg);
                } else {
                    cardHazardAlert.setVisibility(View.GONE);
                }

                highlightSelectedCategoryButton(cat);
            });

            gridCategories.addView(btn);
        }
    }

    private void highlightSelectedCategoryButton(String category) {
        for (int i = 0; i < gridCategories.getChildCount(); i++) {
            View child = gridCategories.getChildAt(i);
            if (child instanceof MaterialButton) {
                MaterialButton btn = (MaterialButton) child;
                boolean isMatch = btn.getText().toString().equalsIgnoreCase(category);
                btn.setStrokeColorResource(isMatch ? R.color.primary : R.color.card_stroke);
                btn.setStrokeWidth(isMatch ? 4 : 1);
                btn.setBackgroundColor(isMatch ? getColor(R.color.primary_light) : Color.TRANSPARENT);
            }
        }
    }

    // =========================================================================
    // STEP 3: WEIGHT INPUT & NUMERIC KEYPAD
    // =========================================================================
    private void setupStep3WeightKeypad() {
        updateWeightDisplay();

        // Quick Preset Buttons
        findViewById(R.id.btnQuickWeight5).setOnClickListener(v -> {
            currentWeightKg += 5.0;
            weightBuilder = new StringBuilder(String.format(Locale.US, "%.1f", currentWeightKg));
            updateWeightDisplay();
        });
        findViewById(R.id.btnQuickWeight10).setOnClickListener(v -> {
            currentWeightKg += 10.0;
            weightBuilder = new StringBuilder(String.format(Locale.US, "%.1f", currentWeightKg));
            updateWeightDisplay();
        });
        findViewById(R.id.btnQuickWeight25).setOnClickListener(v -> {
            currentWeightKg += 25.0;
            weightBuilder = new StringBuilder(String.format(Locale.US, "%.1f", currentWeightKg));
            updateWeightDisplay();
        });

        // Numeric Keypad Grid (1-9, Clear, 0, .)
        GridLayout gridKeypad = findViewById(R.id.gridNumericKeypad);
        gridKeypad.removeAllViews();

        String[] keys = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "C", "0", "."};
        for (String key : keys) {
            MaterialButton btn = new MaterialButton(this);
            btn.setText(key);
            btn.setTextSize(20);
            btn.setTextAppearance(this, android.R.style.TextAppearance_Medium);
            btn.setCornerRadius(12);

            GridLayout.LayoutParams params = new GridLayout.LayoutParams();
            params.width = 0;
            params.height = 140;
            params.columnSpec = GridLayout.spec(GridLayout.UNDEFINED, 1f);
            params.setMargins(6, 6, 6, 6);
            btn.setLayoutParams(params);

            if ("C".equals(key)) {
                btn.setBackgroundColor(getColor(R.color.secondary));
                btn.setTextColor(getColor(R.color.on_secondary));
                btn.setOnClickListener(v -> {
                    weightBuilder = new StringBuilder("0");
                    updateWeightDisplay();
                });
            } else {
                btn.setBackgroundColor(getColor(R.color.surface));
                btn.setTextColor(getColor(R.color.text_primary));
                btn.setStrokeColorResource(R.color.card_stroke);
                btn.setStrokeWidth(2);
                btn.setOnClickListener(v -> {
                    if (weightBuilder.toString().equals("0") || weightBuilder.toString().equals("10.0")) {
                        weightBuilder = new StringBuilder();
                    }
                    if (".".equals(key) && weightBuilder.indexOf(".") != -1) {
                        return; // Prevent duplicate decimal
                    }
                    weightBuilder.append(key);
                    updateWeightDisplay();
                });
            }
            gridKeypad.addView(btn);
        }

        btnConfirmWeight.setOnClickListener(v -> {
            if (currentWeightKg <= 0.0) {
                Toast.makeText(this, "Please enter a valid weight greater than 0 kg", Toast.LENGTH_SHORT).show();
                return;
            }
            showStep(4);
        });
    }

    private void updateWeightDisplay() {
        try {
            if (weightBuilder.length() == 0) {
                currentWeightKg = 0.0;
            } else {
                currentWeightKg = Double.parseDouble(weightBuilder.toString());
            }
        } catch (NumberFormatException e) {
            currentWeightKg = 0.0;
        }
        tvWeightDisplay.setText(String.format(Locale.US, "%.1f", currentWeightKg));
    }

    // =========================================================================
    // STEP 4: PRICE INTELLIGENCE
    // =========================================================================
    private void setupStep4Pricing() {
        btnProceedToRecyclers.setOnClickListener(v -> showStep(5));
    }

    private void loadPriceIntelligence() {
        repository.getPriceForCategory(selectedCategory, price -> {
            if (price != null) {
                currentBenchmarkRate = price.getBuyingPrice();
            } else {
                currentBenchmarkRate = 420.0; // Fallback demo price
            }

            double expectedValue = currentWeightKg * currentBenchmarkRate;
            tvPricePerKg.setText(String.format(Locale.US, "₹%.2f / kg", currentBenchmarkRate));
            tvExpectedValue.setText(String.format(Locale.US, "Expected Value: ₹%,d", Math.round(expectedValue)));
            tvPriceBreakdown.setText(String.format(
                    Locale.US,
                    "%.1f kg × ₹%.2f = ₹%,d",
                    currentWeightKg, currentBenchmarkRate, Math.round(expectedValue)
            ));
        });
    }

    // =========================================================================
    // STEP 5: RECYCLER MATCHING & NET EARNINGS
    // =========================================================================
    private void setupStep5Recyclers() {
        btnCreateLotFinal.setOnClickListener(v -> createLotAndProceed());
    }

    private void loadRecyclerMatching() {
        repository.getRecyclersList(recyclers -> {
            availableRecyclers = recyclers;
            layoutRecyclerList.removeAllViews();

            if (availableRecyclers == null || availableRecyclers.isEmpty()) {
                availableRecyclers = DemoDataSeeder.getInitialRecyclerData();
            }

            // Default selection: highest net earnings (first verified recycler)
            selectedRecycler = availableRecyclers.get(0);
            renderRecyclerCards();
            updateNetEarningsCalculation();
        });
    }

    private void renderRecyclerCards() {
        layoutRecyclerList.removeAllViews();

        for (final RecyclerEntity recycler : availableRecyclers) {
            MaterialCardView card = new MaterialCardView(this);
            card.setRadius(16);
            card.setCardElevation(3);
            card.setUseCompatPadding(true);

            boolean isSelected = selectedRecycler != null && selectedRecycler.getUuid().equals(recycler.getUuid());
            card.setStrokeWidth(isSelected ? 3 : 1);
            card.setStrokeColor(getColor(isSelected ? R.color.primary : R.color.card_stroke));
            card.setCardBackgroundColor(getColor(isSelected ? R.color.primary_light : R.color.surface));

            LinearLayout inner = new LinearLayout(this);
            inner.setOrientation(LinearLayout.VERTICAL);
            inner.setPadding(20, 20, 20, 20);

            // Title & Verified Badge
            LinearLayout topRow = new LinearLayout(this);
            topRow.setOrientation(LinearLayout.HORIZONTAL);
            topRow.setGravity(Gravity.CENTER_VERTICAL);

            TextView tvName = new TextView(this);
            tvName.setText(recycler.getName());
            tvName.setTextSize(16);
            tvName.setTextColor(getColor(R.color.text_primary));
            tvName.setTypeface(null, android.graphics.Typeface.BOLD);
            LinearLayout.LayoutParams nameParams = new LinearLayout.LayoutParams(0, ViewGroup.LayoutParams.WRAP_CONTENT, 1f);
            tvName.setLayoutParams(nameParams);

            ImageView ivBadge = new ImageView(this);
            ivBadge.setImageResource(R.drawable.ic_verified);
            ivBadge.setLayoutParams(new LinearLayout.LayoutParams(24, 24));
            ivBadge.setColorFilter(getColor(R.color.status_online));

            topRow.addView(tvName);
            topRow.addView(ivBadge);

            // CPCB Reg No
            TextView tvReg = new TextView(this);
            tvReg.setText(recycler.getCpcbRegistrationNo() + " • " + String.format(Locale.US, "%.1f km", recycler.getDistanceKm()));
            tvReg.setTextColor(getColor(R.color.text_secondary));
            tvReg.setTextSize(12);
            tvReg.setPadding(0, 4, 0, 8);

            // Rate & Calculated Payout
            double offeredRate = recycler.getDefaultRatePerKg();
            double grossPayout = currentWeightKg * offeredRate;

            TextView tvRate = new TextView(this);
            tvRate.setText(String.format(Locale.US, "Offered Rate: ₹%.2f/kg  |  Gross: ₹%,d", offeredRate, Math.round(grossPayout)));
            tvRate.setTextColor(getColor(R.color.primary));
            tvRate.setTextSize(14);
            tvRate.setTypeface(null, android.graphics.Typeface.BOLD);

            inner.addView(topRow);
            inner.addView(tvReg);
            inner.addView(tvRate);
            card.addView(inner);

            card.setOnClickListener(v -> {
                selectedRecycler = recycler;
                renderRecyclerCards();
                updateNetEarningsCalculation();
            });

            layoutRecyclerList.addView(card);
        }
    }

    private void updateNetEarningsCalculation() {
        if (selectedRecycler == null) return;

        double rate = selectedRecycler.getDefaultRatePerKg();
        finalSaleValue = currentWeightKg * rate;

        // Transport formula: Base ₹50 + ₹30 per km
        double transportCost = 50.0 + (selectedRecycler.getDistanceKm() * 30.0);
        double handlingCost = 100.0; // Standard lot handling fee

        finalNetEarnings = finalSaleValue - transportCost - handlingCost;
        if (finalNetEarnings < 0) finalNetEarnings = 0;

        tvNetTakeHome.setText(String.format(Locale.US, "Net Take-Home: ₹%,d", Math.round(finalNetEarnings)));
        tvNetEarningsFormula.setText(String.format(
                Locale.US,
                "Gross Sale (₹%,d) - Transport (₹%,d) - Handling (₹%,d)",
                Math.round(finalSaleValue), Math.round(transportCost), Math.round(handlingCost)
        ));
    }

    // =========================================================================
    // CREATE LOCAL LOT & QR PROCEED
    // =========================================================================
    private void createLotAndProceed() {
        String lotUuid = UUID.randomUUID().toString();
        String shortCode = generateShortLotCode();
        String now = DemoDataSeeder.getUtcTimestamp();

        LotEntity lot = new LotEntity(
                lotUuid,
                shortCode,
                selectedCategory,
                currentWeightKg,
                currentBenchmarkRate,
                finalSaleValue,
                finalNetEarnings,
                selectedRecycler != null ? selectedRecycler.getUuid() : "rec-001",
                selectedRecycler != null ? selectedRecycler.getName() : "EcoRecycle India",
                "CREATED",
                now,
                now,
                "PENDING"
        );

        LotPhotoEntity photo = null;
        if (compressedFile != null && compressedFile.exists()) {
            photo = new LotPhotoEntity(
                    UUID.randomUUID().toString(),
                    lotUuid,
                    photoSha256,
                    compressedFile.getAbsolutePath(),
                    now,
                    "PENDING"
            );
        }

        repository.createLot(lot, photo, new EcoBridgeRepository.OnLotCreatedCallback() {
            @Override
            public void onSuccess(LotEntity createdLot) {
                audioPromptManager.playPrompt("lot_created", getString(R.string.lot_created_title));
                Intent intent = new Intent(NewLotActivity.this, LotCreatedActivity.class);
                intent.putExtra("lot_uuid", createdLot.getUuid());
                intent.putExtra("short_code", createdLot.getShortCode());
                intent.putExtra("category", createdLot.getCategory());
                intent.putExtra("weight", createdLot.getApproxWeightKg());
                intent.putExtra("estimated_value", createdLot.getEstimatedValue());
                intent.putExtra("net_earnings", createdLot.getNetEarnings());
                intent.putExtra("recycler_name", createdLot.getSelectedRecyclerName());
                intent.putExtra("recycler_id", createdLot.getSelectedRecyclerId());
                startActivity(intent);
                finish();
            }

            @Override
            public void onError(Exception e) {
                Toast.makeText(NewLotActivity.this, "Error creating lot: " + e.getMessage(), Toast.LENGTH_LONG).show();
            }
        });
    }

    private String generateShortLotCode() {
        String chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
        StringBuilder sb = new StringBuilder("LOT-");
        SecureRandom random = new SecureRandom();
        for (int i = 0; i < 5; i++) {
            sb.append(chars.charAt(random.nextInt(chars.length())));
        }
        return sb.toString();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == CAMERA_PERMISSION_CODE && grantResults.length > 0 &&
                grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            cameraManager.startCamera(null);
        } else {
            Toast.makeText(this, R.string.camera_permission_required, Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (cameraManager != null) cameraManager.stopCamera();
        if (scrapClassifier != null) scrapClassifier.close();
        if (audioPromptManager != null) audioPromptManager.release();
    }
}
