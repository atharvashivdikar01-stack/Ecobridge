package com.ecobridge.ui.recycler;

import android.os.Bundle;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.R;
import com.ecobridge.data.local.entity.RecyclerEntity;
import com.ecobridge.data.repository.DemoDataSeeder;
import com.ecobridge.data.repository.EcoBridgeRepository;
import com.ecobridge.ui.BaseActivity;
import com.google.android.material.appbar.MaterialToolbar;
import com.google.android.material.card.MaterialCardView;

import java.util.List;
import java.util.Locale;

public class RecyclersActivity extends BaseActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        EcoBridgeApplication.getInstance().applyLocale(
                EcoBridgeApplication.getInstance().getSavedLanguage()
        );
        setContentView(R.layout.activity_recyclers);
        MaterialToolbar toolbar = findViewById(R.id.toolbar);
        toolbar.setNavigationOnClickListener(v -> finish());
        LinearLayout list = findViewById(R.id.layoutRecyclerList);
        EcoBridgeRepository repository = EcoBridgeApplication.getInstance().getRepository();
        repository.getRecyclersList(recyclers -> render(list, recyclers));
    }

    private void render(LinearLayout list, List<RecyclerEntity> recyclers) {
        if (recyclers == null || recyclers.isEmpty()) {
            recyclers = DemoDataSeeder.getInitialRecyclerData();
        }
        list.removeAllViews();
        for (RecyclerEntity recycler : recyclers) {
            MaterialCardView card = new MaterialCardView(this);
            card.setRadius(16);
            card.setUseCompatPadding(true);
            LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                    LinearLayout.LayoutParams.MATCH_PARENT,
                    LinearLayout.LayoutParams.WRAP_CONTENT
            );
            params.bottomMargin = 16;
            card.setLayoutParams(params);
            LinearLayout inner = new LinearLayout(this);
            inner.setOrientation(LinearLayout.VERTICAL);
            inner.setPadding(32, 32, 32, 32);
            TextView name = new TextView(this);
            name.setText(recycler.getName());
            name.setTextSize(18);
            name.setTypeface(null, android.graphics.Typeface.BOLD);
            TextView detail = new TextView(this);
            detail.setText(String.format(Locale.US, "%s • %.1f km • ₹%.0f/kg",
                    recycler.getCpcbRegistrationNo(), recycler.getDistanceKm(), recycler.getDefaultRatePerKg()));
            inner.addView(name);
            inner.addView(detail);
            card.addView(inner);
            list.addView(card);
        }
    }
}
