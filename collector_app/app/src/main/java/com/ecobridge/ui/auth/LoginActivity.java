package com.ecobridge.ui.auth;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Toast;
import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.R;
import com.ecobridge.data.local.AppDatabase;
import com.ecobridge.data.local.TokenStore;
import com.ecobridge.data.remote.RetrofitClient;
import com.ecobridge.data.remote.dto.ApiResponseDto;
import com.ecobridge.data.remote.dto.OtpRequest;
import com.ecobridge.data.remote.dto.TokenResponseDto;
import com.ecobridge.data.remote.dto.VerifyOtpRequest;
import com.ecobridge.ui.BaseActivity;
import com.ecobridge.ui.home.HomeActivity;
import com.google.android.material.button.MaterialButton;
import com.google.android.material.textfield.TextInputEditText;
import retrofit2.Response;

public class LoginActivity extends BaseActivity {
    private TextInputEditText phone, otp;
    @Override protected void onCreate(Bundle state) {
        super.onCreate(state); setContentView(R.layout.activity_login);
        phone = findViewById(R.id.inputPhone); otp = findViewById(R.id.inputOtp);
        findViewById(R.id.btnSendOtp).setOnClickListener(v -> sendOtp());
        findViewById(R.id.btnVerifyOtp).setOnClickListener(v -> verifyOtp());
        findViewById(R.id.btnContinueOffline).setOnClickListener(v -> openHome());
    }
    private String number() { String digits = phone.getText() == null ? "" : phone.getText().toString().replaceAll("\\D", ""); return digits.length() == 10 ? "+91" + digits : null; }
    private void sendOtp() {
        String number = number(); if (number == null) { phone.setError("Enter 10 digits"); return; }
        AppDatabase.databaseWriteExecutor.execute(() -> { try {
            Response<ApiResponseDto<Object>> result = RetrofitClient.getApiService().sendOtp(new OtpRequest(number)).execute();
            runOnUiThread(() -> Toast.makeText(this, result.isSuccessful() ? "OTP sent" : "OTP unavailable", Toast.LENGTH_SHORT).show());
        } catch (Exception e) { runOnUiThread(() -> Toast.makeText(this, "No network. Continue offline.", Toast.LENGTH_LONG).show()); } });
    }
    private void verifyOtp() {
        String number = number(); String code = otp.getText() == null ? "" : otp.getText().toString().trim();
        if (number == null || code.length() != 6) { Toast.makeText(this, "Enter mobile number and 6-digit OTP", Toast.LENGTH_SHORT).show(); return; }
        AppDatabase.databaseWriteExecutor.execute(() -> { try {
            Response<ApiResponseDto<TokenResponseDto>> result = RetrofitClient.getApiService().verifyOtp(new VerifyOtpRequest(number, code, EcoBridgeApplication.getInstance().getSavedLanguage())).execute();
            TokenResponseDto token = result.body() == null ? null : result.body().getData();
            if (result.isSuccessful() && result.body().isSuccess() && token != null && token.getAccessToken() != null) { TokenStore.save(this, token.getAccessToken(), token.getRefreshToken()); runOnUiThread(this::openHome); }
            else runOnUiThread(() -> Toast.makeText(this, "OTP verification failed", Toast.LENGTH_SHORT).show());
        } catch (Exception e) { runOnUiThread(() -> Toast.makeText(this, "No network. Continue offline.", Toast.LENGTH_LONG).show()); } });
    }
    private void openHome() { startActivity(new Intent(this, HomeActivity.class)); finish(); }
}
