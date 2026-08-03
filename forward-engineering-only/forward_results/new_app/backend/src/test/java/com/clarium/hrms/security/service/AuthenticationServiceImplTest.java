package com.clarium.hrms.security.service;

import com.clarium.hrms.common.exception.AuthenticationFailedException;
import com.clarium.hrms.security.domain.RefreshToken;
import com.clarium.hrms.security.domain.Role;
import com.clarium.hrms.security.domain.UserCredential;
import com.clarium.hrms.security.dto.AuthResponse;
import com.clarium.hrms.security.dto.LoginRequest;
import com.clarium.hrms.security.jwt.JwtProperties;
import com.clarium.hrms.security.jwt.JwtTokenProvider;
import com.clarium.hrms.security.repository.RefreshTokenRepository;
import com.clarium.hrms.security.repository.UserCredentialRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.Instant;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class AuthenticationServiceImplTest {

    @Mock
    private UserCredentialRepository userCredentialRepository;
    @Mock
    private RefreshTokenRepository refreshTokenRepository;
    @Mock
    private org.springframework.security.crypto.password.PasswordEncoder passwordEncoder;
    @Mock
    private JwtTokenProvider jwtTokenProvider;

    private JwtProperties jwtProperties;
    private AuthenticationServiceImpl service;

    @BeforeEach
    void setUp() {
        jwtProperties = new JwtProperties();
        jwtProperties.setAccessTokenTtlSeconds(900);
        jwtProperties.setRefreshTokenTtlSeconds(604800);
        service = new AuthenticationServiceImpl(
                userCredentialRepository, refreshTokenRepository, passwordEncoder, jwtTokenProvider, jwtProperties);
    }

    private UserCredential user() {
        UserCredential u = new UserCredential();
        u.setId(1L);
        u.setEmail("jane.doe@example.com");
        u.setPasswordHash("hashed");
        u.setEmployeeId(42L);
        u.setRole(Role.EMPLOYEE);
        u.setFailedAttempts(0);
        return u;
    }

    @Test
    void should_returnTokens_when_credentialsAreValid() {
        UserCredential u = user();
        when(userCredentialRepository.findByEmail("jane.doe@example.com")).thenReturn(Optional.of(u));
        when(passwordEncoder.matches("correct-password", "hashed")).thenReturn(true);
        when(jwtTokenProvider.generateAccessToken(u)).thenReturn("access-token");
        when(jwtTokenProvider.generateRefreshToken(u)).thenReturn("refresh-token");

        AuthResponse response = service.login(new LoginRequest("jane.doe@example.com", "correct-password"));

        assertThat(response.accessToken()).isEqualTo("access-token");
        assertThat(response.refreshToken()).isEqualTo("refresh-token");
        assertThat(response.employeeId()).isEqualTo(42L);
        assertThat(u.getFailedAttempts()).isZero();
        verify(refreshTokenRepository).save(any(RefreshToken.class));
    }

    @Test
    void should_throwAuthenticationFailed_when_passwordIsWrong() {
        UserCredential u = user();
        when(userCredentialRepository.findByEmail("jane.doe@example.com")).thenReturn(Optional.of(u));
        when(passwordEncoder.matches("wrong-password", "hashed")).thenReturn(false);

        assertThatThrownBy(() -> service.login(new LoginRequest("jane.doe@example.com", "wrong-password")))
                .isInstanceOf(AuthenticationFailedException.class);

        assertThat(u.getFailedAttempts()).isEqualTo(1);
        verify(jwtTokenProvider, never()).generateAccessToken(any());
    }

    @Test
    void should_lockAccount_when_fifthConsecutiveFailedAttemptOccurs() {
        UserCredential u = user();
        u.setFailedAttempts(4);
        when(userCredentialRepository.findByEmail("jane.doe@example.com")).thenReturn(Optional.of(u));
        when(passwordEncoder.matches("wrong-password", "hashed")).thenReturn(false);

        assertThatThrownBy(() -> service.login(new LoginRequest("jane.doe@example.com", "wrong-password")))
                .isInstanceOf(AuthenticationFailedException.class);

        assertThat(u.getFailedAttempts()).isEqualTo(5);
        assertThat(u.getLockedUntil()).isAfter(Instant.now());
    }

    @Test
    void should_rejectLogin_when_accountIsCurrentlyLocked() {
        UserCredential u = user();
        u.setLockedUntil(Instant.now().plusSeconds(600));
        when(userCredentialRepository.findByEmail("jane.doe@example.com")).thenReturn(Optional.of(u));

        assertThatThrownBy(() -> service.login(new LoginRequest("jane.doe@example.com", "any-password")))
                .isInstanceOf(AuthenticationFailedException.class);

        verify(passwordEncoder, never()).matches(any(), any());
    }
}
