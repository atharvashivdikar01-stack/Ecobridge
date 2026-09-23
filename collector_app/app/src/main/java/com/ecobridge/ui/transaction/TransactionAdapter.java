package com.ecobridge.ui.transaction;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.ecobridge.R;
import com.ecobridge.data.local.entity.LotEntity;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * TransactionAdapter
 * RecyclerView adapter for displaying transaction cards in the ledger.
 */
public class TransactionAdapter extends RecyclerView.Adapter<TransactionAdapter.TransactionViewHolder> {

    private List<LotEntity> transactions = new ArrayList<>();
    private OnTransactionClickListener listener;

    public interface OnTransactionClickListener {
        void onTransactionClick(LotEntity lot);
    }

    public TransactionAdapter(OnTransactionClickListener listener) {
        this.listener = listener;
    }

    public void setTransactions(List<LotEntity> transactions) {
        this.transactions = transactions;
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public TransactionViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_transaction, parent, false);
        return new TransactionViewHolder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull TransactionViewHolder holder, int position) {
        LotEntity lot = transactions.get(position);
        holder.bind(lot, listener);
    }

    @Override
    public int getItemCount() {
        return transactions.size();
    }

    static class TransactionViewHolder extends RecyclerView.ViewHolder {
        private TextView tvLotCode;
        private TextView tvMaterialWeight;
        private TextView tvRecycler;
        private TextView tvAmount;
        private TextView tvPayment;
        private TextView tvDate;
        private TextView tvSyncStatus;

        public TransactionViewHolder(@NonNull View itemView) {
            super(itemView);
            tvLotCode = itemView.findViewById(R.id.tvItemLotCode);
            tvMaterialWeight = itemView.findViewById(R.id.tvItemMaterialWeight);
            tvRecycler = itemView.findViewById(R.id.tvItemRecycler);
            tvAmount = itemView.findViewById(R.id.tvItemAmount);
            tvPayment = itemView.findViewById(R.id.tvItemPayment);
            tvDate = itemView.findViewById(R.id.tvItemDate);
            tvSyncStatus = itemView.findViewById(R.id.tvItemSyncStatus);
        }

        public void bind(LotEntity lot, OnTransactionClickListener listener) {
            tvLotCode.setText(lot.getShortCode());
            tvMaterialWeight.setText(String.format(Locale.US, "%s • %.1f kg", lot.getCategory(), lot.getApproxWeightKg()));
            tvRecycler.setText(lot.getSelectedRecyclerName());
            tvAmount.setText(String.format(Locale.US, "₹%,d", Math.round(lot.getEstimatedValue())));
            tvDate.setText(lot.getCreatedAt().substring(0, 10)); // Show just the date

            String syncStatus = lot.getSyncStatus();
            tvSyncStatus.setText(syncStatus);

            if ("SYNCED".equals(syncStatus)) {
                tvSyncStatus.setTextColor(itemView.getContext().getColor(R.color.status_online));
            } else {
                tvSyncStatus.setTextColor(itemView.getContext().getColor(R.color.status_pending));
            }

            itemView.setOnClickListener(v -> listener.onTransactionClick(lot));
        }
    }
}