package com.clarium.hrms.security.service;

import com.clarium.hrms.common.exception.AuthenticationFailedException;
import com.clarium.hrms.security.domain.UserCredential;
import com.clarium.hrms.security.dto.AuthResponse;
import com.clarium.hrms.security.dto.LoginRequest;
import com.clarium.hrms.security.dto.RefreshTokenRequest;
import com.clarium.hrms.security.jwt.JwtProperties;
import com.clarium.hrms.security.jwt.JwtTokenProvider;
import com.clarium.hrms.security.jwt.TokenType;
import com.clarium.hrms.security.repository.UserCredentialRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;

@Service
@RequiredArgsConstructor
public class AuthenticationServiceImpl implements AuthenticationService {

    private static final int MAX_FAILED_LOGIN_ATTEMPTS = 5;
    private static final String INVALID_CREDENTIALS_MESSAGE = "Invalid email or password";
    private static final String ACCOUNT_LOCKED_MESSAGE = "Account is locked due to repeated failed login attempts";
    private static final String INVALID_REFRESH_TOKEN_MESSAGE = "Invalid or expired refresh token";

    private final UserCredentialRepository userCredentialRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider jwtTokenProvider;
    private final JwtProperties jwtProperties;

    @Override
    @Transactional
    public AuthResponse login(LoginRequest request) {
        UserCredential credential = userCredentialRepository.findByEmail(request.email())
                .orElseThrow(() -> new AuthenticationFailedException(INVALID_CREDENTIALS_MESSAGE));

        if (credential.isAccountLocked()) {
            throw new AuthenticationFailedException(ACCOUNT_LOCKED_MESSAGE);
        }

        if (!passwordEncoder.matches(request.password(), credential.getPasswordHash())) {
            registerFailedAttempt(credential);
            throw new AuthenticationFailedException(INVALID_CREDENTIALS_MESSAGE);
        }

        credential.setFailedLoginAttempts(0);
        credential.setLastLoginAt(Instant.now());
        userCredentialRepository.save(credential);

        return issueTokens(credential);
    }

    @Override
    @Transactional
    public AuthResponse refresh(RefreshTokenRequest request) {
        String email = jwtTokenProvider.parseSubject(request.refreshToken(), TokenType.REFRESH)
                .orElseThrow(() -> new AuthenticationFailedException(INVALID_REFRESH_TOKEN_MESSAGE));

        UserCredential credential = userCredentialRepository.findByEmail(email)
                .orElseThrow(() -> new AuthenticationFailedException(INVALID_REFRESH_TOKEN_MESSAGE));

        if (credential.isAccountLocked()) {
            throw new AuthenticationFailedException(ACCOUNT_LOCKED_MESSAGE);
        }

        return issueTokens(credential);
    }

    @Override
    public void logout(String authorizationHeader) {
        // Stateless JWTs carry no server-side session to revoke; the client discards its tokens.
    }

    private void registerFailedAttempt(UserCredential credential) {
        int attempts = credential.getFailedLoginAttempts() + 1;
        credential.setFailedLoginAttempts(attempts);
        if (attempts >= MAX_FAILED_LOGIN_ATTEMPTS) {
            credential.setAccountLocked(true);
        }
        userCredentialRepository.save(credential);
    }

    private AuthResponse issueTokens(UserCredential credential) {
        String accessToken = jwtTokenProvider.generateToken(credential, TokenType.ACCESS);
        String refreshToken = jwtTokenProvider.generateToken(credential, TokenType.REFRESH);
        return new AuthResponse(accessToken, refreshToken, jwtProperties.accessTokenTtlSeconds());
    }
}
