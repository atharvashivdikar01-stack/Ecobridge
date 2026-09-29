package com.ecobridge.ui.auth;

import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.Toast;
import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.R;
import com.ecobridge.data.local.AppDatabase;
import com.ecobridge.data.local.TokenStore;
import com.ecobridge.data.remote.RetrofitClient;
import com.ecobridge.data.remote.dto.ApiResponseDto;
import com.ecobridge.data.remote.dto.DemoLoginRequest;
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
        if (phone != null && (phone.getText() == null || phone.getText().toString().isEmpty())) {
            phone.setText("9800000001");
        }
        if (otp != null && (otp.getText() == null || otp.getText().toString().isEmpty())) {
            otp.setText("123456");
        }
        findViewById(R.id.btnSendOtp).setOnClickListener(v -> sendOtp());
        findViewById(R.id.btnVerifyOtp).setOnClickListener(v -> verifyOtp());
        View btnQuickDemo = findViewById(R.id.btnQuickDemoLogin);
        if (btnQuickDemo != null) {
            btnQuickDemo.setOnClickListener(v -> quickDemoLogin());
        }
        findViewById(R.id.btnContinueOffline).setOnClickListener(v -> openHome());

        View.OnClickListener langClick = v -> startActivity(new Intent(this, com.ecobridge.ui.settings.LanguageActivity.class));
        View cardLang = findViewById(R.id.cardLanguageSelect);
        if (cardLang != null) cardLang.setOnClickListener(langClick);
        View btnLang = findViewById(R.id.btnChangeLanguage);
        if (btnLang != null) btnLang.setOnClickListener(langClick);
    }
    private String number() { String digits = phone.getText() == null ? "" : phone.getText().toString().replaceAll("\\D", ""); return digits.length() == 10 ? "+91" + digits : null; }
    private void sendOtp() {
        String number = number(); if (number == null) { phone.setError("Enter 10 digits"); return; }
        Toast.makeText(this, "Connecting to server...", Toast.LENGTH_SHORT).show();
        AppDatabase.databaseWriteExecutor.execute(() -> { try {
            Response<ApiResponseDto<Object>> result = RetrofitClient.getApiService().sendOtp(new OtpRequest(number)).execute();
            runOnUiThread(() -> Toast.makeText(this, result.isSuccessful() ? "OTP sent to " + number : "OTP service busy, try 123456", Toast.LENGTH_SHORT).show());
        } catch (Exception e) {
            android.util.Log.e("LoginActivity", "Send OTP failed", e);
            runOnUiThread(() -> Toast.makeText(this, "Network error: " + e.getMessage(), Toast.LENGTH_LONG).show());
        } });
    }
    private void verifyOtp() {
        String number = number(); String code = otp.getText() == null ? "" : otp.getText().toString().trim();
        if (number == null || code.length() != 6) { Toast.makeText(this, "Enter mobile number and 6-digit OTP", Toast.LENGTH_SHORT).show(); return; }
        Toast.makeText(this, "Verifying OTP online...", Toast.LENGTH_SHORT).show();
        AppDatabase.databaseWriteExecutor.execute(() -> { try {
            Response<ApiResponseDto<TokenResponseDto>> result = RetrofitClient.getApiService().verifyOtp(new VerifyOtpRequest(number, code, EcoBridgeApplication.getInstance().getSavedLanguage())).execute();
            TokenResponseDto token = result.body() == null ? null : result.body().getData();
            if (result.isSuccessful() && result.body().isSuccess() && token != null && token.getAccessToken() != null) {
                TokenStore.save(this, token.getAccessToken(), token.getRefreshToken());
                com.ecobridge.sync.SyncWorker.triggerImmediateSync(this);
                runOnUiThread(this::openHome);
            } else {
                runOnUiThread(() -> Toast.makeText(this, "OTP verification failed. Use 123456 or 1-Click Login.", Toast.LENGTH_SHORT).show());
            }
        } catch (Exception e) {
            android.util.Log.e("LoginActivity", "Verify OTP failed", e);
            runOnUiThread(() -> Toast.makeText(this, "Network error: " + e.getMessage(), Toast.LENGTH_LONG).show());
        } });
    }
    private void quickDemoLogin() {
        Toast.makeText(this, "Logging in as Raju Shinde...", Toast.LENGTH_SHORT).show();
        AppDatabase.databaseWriteExecutor.execute(() -> {
            try {
                // Try demo login route first
                Response<ApiResponseDto<TokenResponseDto>> result = RetrofitClient.getApiService()
                        .demoLogin(new DemoLoginRequest("COLLECTOR")).execute();
                TokenResponseDto token = result.body() == null ? null : result.body().getData();
                if (result.isSuccessful() && token != null && token.getAccessToken() != null) {
                    TokenStore.save(this, token.getAccessToken(), token.getRefreshToken());
                    com.ecobridge.sync.SyncWorker.triggerImmediateSync(this);
                    runOnUiThread(() -> {
                        Toast.makeText(this, "Welcome, Raju Shinde (Online)", Toast.LENGTH_SHORT).show();
                        openHome();
                    });
                    return;
                }

                // Fallback to OTP verify with default demo credentials
                Response<ApiResponseDto<TokenResponseDto>> otpResult = RetrofitClient.getApiService()
                        .verifyOtp(new VerifyOtpRequest("+919800000001", "123456", "en")).execute();
                TokenResponseDto otpToken = otpResult.body() == null ? null : otpResult.body().getData();
                if (otpResult.isSuccessful() && otpToken != null && otpToken.getAccessToken() != null) {
                    TokenStore.save(this, otpToken.getAccessToken(), otpToken.getRefreshToken());
                    com.ecobridge.sync.SyncWorker.triggerImmediateSync(this);
                    runOnUiThread(() -> {
                        Toast.makeText(this, "Welcome, Raju Shinde (Online)", Toast.LENGTH_SHORT).show();
                        openHome();
                    });
                    return;
                }

                runOnUiThread(() -> Toast.makeText(this, "Login rejected by server.", Toast.LENGTH_SHORT).show());
            } catch (Exception e) {
                android.util.Log.e("LoginActivity", "Quick demo login failed", e);
                runOnUiThread(() -> Toast.makeText(this, "Network error: " + e.getMessage(), Toast.LENGTH_LONG).show());
            }
        });
    }
    private void openHome() { startActivity(new Intent(this, HomeActivity.class)); finish(); }
}
