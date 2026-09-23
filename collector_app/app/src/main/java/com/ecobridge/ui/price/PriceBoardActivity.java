package com.ecobridge.ui.price;

import android.os.Bundle;
import android.view.View;
import android.widget.TextView;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.R;
import com.ecobridge.data.local.entity.PriceEntity;
import com.ecobridge.data.repository.EcoBridgeRepository;

import com.ecobridge.ui.BaseActivity;
import com.google.android.material.appbar.MaterialToolbar;

import java.util.List;

/**
 * PriceBoardActivity
 * Displays current benchmark prices for all scrap material categories.
 * Prices are cached locally for offline access.
 */
public class PriceBoardActivity extends BaseActivity {

    private EcoBridgeRepository repository;
    private RecyclerView recyclerView;
    private TextView tvLastUpdated;
    private TextView tvEmptyState;
    private PriceAdapter adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EcoBridgeApplication.getInstance().applyLocale(
                EcoBridgeApplication.getInstance().getSavedLanguage()
        );
        setContentView(R.layout.activity_price_board);

        repository = EcoBridgeApplication.getInstance().getRepository();

        initViews();
        loadPrices();
    }

    private void initViews() {
        MaterialToolbar toolbar = findViewById(R.id.toolbar);
        if (toolbar != null) {
            toolbar.setNavigationOnClickListener(v -> finish());
        }

        recyclerView = findViewById(R.id.recyclerViewPrices);
        tvLastUpdated = findViewById(R.id.tvLastUpdated);
        tvEmptyState = findViewById(R.id.tvEmptyState);

        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        adapter = new PriceAdapter();
        recyclerView.setAdapter(adapter);
    }

    private void loadPrices() {
        repository.getAllPrices(prices -> {
            runOnUiThread(() -> {
                if (prices == null || prices.isEmpty()) {
                    tvEmptyState.setVisibility(View.VISIBLE);
                    recyclerView.setVisibility(View.GONE);
                } else {
                    tvEmptyState.setVisibility(View.GONE);
                    recyclerView.setVisibility(View.VISIBLE);
                    adapter.setPrices(prices);

                    // Show last updated timestamp
                    if (!prices.isEmpty()) {
                        String lastUpdate = prices.get(0).getUpdatedAt();
                        tvLastUpdated.setText("Last updated: " + lastUpdate);
                    }
                }
            });
        });
    }
}
