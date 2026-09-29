package com.ecobridge.data.remote.dto;

public class DemoLoginRequest {
    private final String role;

    public DemoLoginRequest(String role) {
        this.role = role;
    }

    public String getRole() {
        return role;
    }
}
