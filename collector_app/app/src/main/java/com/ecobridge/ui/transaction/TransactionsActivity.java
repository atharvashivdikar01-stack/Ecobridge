package com.ecobridge.ui.transaction;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.R;
import com.ecobridge.data.local.entity.LotEntity;
import com.ecobridge.data.repository.EcoBridgeRepository;
import com.ecobridge.ui.BaseActivity;
import com.google.android.material.appbar.MaterialToolbar;

import java.util.List;

/**
 * TransactionsActivity
 * Displays the collector's transaction ledger with all local lots,
 * including sync status, material type, weight, and earnings.
 */
public class TransactionsActivity extends BaseActivity {

    private EcoBridgeRepository repository;
    private RecyclerView recyclerView;
    private TextView tvEmptyState;
    private TransactionAdapter adapter;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EcoBridgeApplication.getInstance().applyLocale(
                EcoBridgeApplication.getInstance().getSavedLanguage()
        );
        setContentView(R.layout.activity_transactions);

        repository = EcoBridgeApplication.getInstance().getRepository();

        initViews();
        loadTransactions();
    }

    private void initViews() {
        MaterialToolbar toolbar = findViewById(R.id.toolbar);
        if (toolbar != null) {
            toolbar.setNavigationOnClickListener(v -> finish());
        }

        recyclerView = findViewById(R.id.recyclerViewTransactions);
        tvEmptyState = findViewById(R.id.tvEmptyState);

        recyclerView.setLayoutManager(new LinearLayoutManager(this));
        adapter = new TransactionAdapter(lot -> {
            Intent intent = new Intent(TransactionsActivity.this, TransactionDetailActivity.class);
            intent.putExtra("lot_uuid", lot.getUuid());
            startActivity(intent);
        });
        recyclerView.setAdapter(adapter);
    }

    private void loadTransactions() {
        repository.getAllLots(lots -> {
            runOnUiThread(() -> {
                if (lots == null || lots.isEmpty()) {
                    tvEmptyState.setVisibility(View.VISIBLE);
                    recyclerView.setVisibility(View.GONE);
                } else {
                    tvEmptyState.setVisibility(View.GONE);
                    recyclerView.setVisibility(View.VISIBLE);
                    adapter.setTransactions(lots);
                }
            });
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        loadTransactions();
    }
}
