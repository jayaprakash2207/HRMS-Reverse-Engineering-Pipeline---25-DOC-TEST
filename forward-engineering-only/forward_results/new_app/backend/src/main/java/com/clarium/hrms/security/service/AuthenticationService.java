package com.clarium.hrms.security.service;

import com.clarium.hrms.security.dto.AuthResponse;
import com.clarium.hrms.security.dto.LoginRequest;
import com.clarium.hrms.security.dto.RefreshTokenRequest;

public interface AuthenticationService {

    AuthResponse login(LoginRequest request);

    AuthResponse refresh(RefreshTokenRequest request);

    void logout(String authorizationHeader);
}
