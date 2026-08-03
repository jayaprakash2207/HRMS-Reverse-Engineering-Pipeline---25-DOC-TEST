package com.clarium.hrms.security.dto;

public record AuthResponse(String accessToken, String refreshToken, long expiresIn) {
}
