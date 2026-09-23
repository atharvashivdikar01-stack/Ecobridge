package com.ecobridge.data.remote.dto;
public class VerifyOtpRequest {
    private final String phone; private final String otp; private final String preferred_language;
    public VerifyOtpRequest(String phone, String otp, String language) { this.phone = phone; this.otp = otp; this.preferred_language = language; }
}
