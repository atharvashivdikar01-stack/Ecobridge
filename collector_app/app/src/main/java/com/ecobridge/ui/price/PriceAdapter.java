package com.ecobridge.ui.price;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.ecobridge.R;
import com.ecobridge.data.local.entity.PriceEntity;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * PriceAdapter
 * RecyclerView adapter for displaying price cards for different material categories.
 */
public class PriceAdapter extends RecyclerView.Adapter<PriceAdapter.PriceViewHolder> {

    private List<PriceEntity> prices = new ArrayList<>();

    public void setPrices(List<PriceEntity> prices) {
        this.prices = prices;
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public PriceViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_price, parent, false);
        return new PriceViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull PriceViewHolder holder, int position) {
        PriceEntity price = prices.get(position);
        holder.bind(price);
    }

    @Override
    public int getItemCount() {
        return prices.size();
    }

    static class PriceViewHolder extends RecyclerView.ViewHolder {
        private TextView tvCategory;
        private TextView tvBuyingPrice;
        private TextView tvSellingPrice;
        private TextView tvRange;
        private TextView tvSource;

        public PriceViewHolder(@NonNull View itemView) {
            super(itemView);
            tvCategory = itemView.findViewById(R.id.tvPriceCategory);
            tvBuyingPrice = itemView.findViewById(R.id.tvPriceBuying);
            tvSellingPrice = itemView.findViewById(R.id.tvPriceSelling);
            tvRange = itemView.findViewById(R.id.tvPriceRange);
            tvSource = itemView.findViewById(R.id.tvPriceSource);
        }

        public void bind(PriceEntity price) {
            tvCategory.setText(price.getCategory());
            tvBuyingPrice.setText(String.format(Locale.US, "Buying: ₹%.2f / kg", price.getBuyingPrice()));
            tvSellingPrice.setText(String.format(Locale.US, "Selling / reference: ₹%.2f / kg", price.getSellingPrice()));
            tvRange.setText(String.format(Locale.US, "Range: ₹%.0f – ₹%.0f", price.getBuyingPrice(), price.getSellingPrice()));
            tvSource.setText("Source: " + price.getSourceType());
        }
    }
}