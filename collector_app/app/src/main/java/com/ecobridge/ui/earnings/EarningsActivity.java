package com.ecobridge.ui.earnings;

import android.os.Bundle;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;

import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.R;
import com.ecobridge.data.repository.EcoBridgeRepository;
import com.ecobridge.ui.BaseActivity;
import com.google.android.material.appbar.MaterialToolbar;

import java.util.Locale;

/**
 * EarningsActivity
 * Displays collector's earnings summary: today, weekly, and total lifetime earnings.
 */
public class EarningsActivity extends BaseActivity {

    private EcoBridgeRepository repository;

    private TextView tvTodayEarnings;
    private TextView tvWeeklyEarnings;
    private TextView tvTotalEarnings;
    private TextView tvTotalLots;
    private TextView tvTotalWeight;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EcoBridgeApplication.getInstance().applyLocale(
                EcoBridgeApplication.getInstance().getSavedLanguage()
        );
        setContentView(R.layout.activity_earnings);

        repository = EcoBridgeApplication.getInstance().getRepository();

        initViews();
        loadEarningsData();
    }

    private void initViews() {
        MaterialToolbar toolbar = findViewById(R.id.toolbar);
        if (toolbar != null) {
            toolbar.setNavigationOnClickListener(v -> finish());
        }

        tvTodayEarnings = findViewById(R.id.tvTodayEarnings);
        tvWeeklyEarnings = findViewById(R.id.tvWeeklyEarnings);
        tvTotalEarnings = findViewById(R.id.tvTotalEarnings);
        tvTotalLots = findViewById(R.id.tvTotalLots);
        tvTotalWeight = findViewById(R.id.tvTotalWeight);
    }

    private void loadEarningsData() {
        repository.getEarningsSummary(summary -> {
            if (summary != null) {
                runOnUiThread(() -> {
                    tvTodayEarnings.setText(String.format(Locale.US, "₹%,d", Math.round(summary.todayEarnings)));
                    tvWeeklyEarnings.setText(String.format(Locale.US, "₹%,d", Math.round(summary.weeklyEarnings)));
                    tvTotalEarnings.setText(String.format(Locale.US, "₹%,d", Math.round(summary.totalEarnings)));
                    tvTotalLots.setText(String.valueOf(summary.totalLots));
                    tvTotalWeight.setText(String.format(Locale.US, "%.1f kg", summary.totalWeight));
                });
            }
        });
    }
}
