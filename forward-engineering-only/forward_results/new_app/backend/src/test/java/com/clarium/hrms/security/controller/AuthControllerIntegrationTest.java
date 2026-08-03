package com.clarium.hrms.security.controller;

import com.clarium.hrms.common.dto.ErrorResponse;
import com.clarium.hrms.security.domain.Role;
import com.clarium.hrms.security.domain.UserCredential;
import com.clarium.hrms.security.dto.AuthResponse;
import com.clarium.hrms.security.dto.LoginRequest;
import com.clarium.hrms.security.dto.RefreshTokenRequest;
import com.clarium.hrms.security.repository.UserCredentialRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.web.server.LocalServerPort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.nio.charset.StandardCharsets;
import java.util.Base64;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class AuthControllerIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine")
            .withDatabaseName("hrms")
            .withUsername("hrms")
            .withPassword("hrms");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
        registry.add("app.security.jwt.secret", () ->
                Base64.getEncoder().encodeToString("integration-test-secret-key-32b!".getBytes(StandardCharsets.UTF_8)));
    }

    @LocalServerPort
    private int port;

    @Autowired
    private TestRestTemplate restTemplate;

    @Autowired
    private UserCredentialRepository userCredentialRepository;

    @Autowired
    private PasswordEncoder passwordEncoder;

    private String baseUrl() {
        return "http://localhost:" + port + "/api/v1/auth";
    }

    private void seedUser(String email, String rawPassword) {
        UserCredential user = new UserCredential();
        user.setEmail(email);
        user.setPasswordHash(passwordEncoder.encode(rawPassword));
        user.setEmployeeId(101L);
        user.setRole(Role.EMPLOYEE);
        userCredentialRepository.save(user);
    }

    @Test
    void should_returnTokens_when_loginWithCorrectCredentials() {
        seedUser("login-ok@example.com", "correct-horse-battery-staple");

        ResponseEntity<AuthResponse> response = restTemplate.postForEntity(
                baseUrl() + "/login",
                new LoginRequest("login-ok@example.com", "correct-horse-battery-staple"),
                AuthResponse.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().accessToken()).isNotBlank();
        assertThat(response.getBody().refreshToken()).isNotBlank();
        assertThat(response.getBody().employeeId()).isEqualTo(101L);
    }

    @Test
    void should_returnUnauthorized_when_passwordIsWrong() {
        seedUser("login-bad@example.com", "correct-horse-battery-staple");

        ResponseEntity<ErrorResponse> response = restTemplate.postForEntity(
                baseUrl() + "/login",
                new LoginRequest("login-bad@example.com", "wrong-password"),
                ErrorResponse.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
        assertThat(response.getBody()).isNotNull();
        assertThat(response.getBody().errorCode()).isEqualTo("AUTHENTICATION_FAILED");
    }

    @Test
    void should_issueNewTokensAndRevokeOldOne_when_refreshTokenIsValid() {
        seedUser("refresh-ok@example.com", "correct-horse-battery-staple");
        AuthResponse login = restTemplate.postForEntity(
                baseUrl() + "/login",
                new LoginRequest("refresh-ok@example.com", "correct-horse-battery-staple"),
                AuthResponse.class).getBody();

        ResponseEntity<AuthResponse> refreshed = restTemplate.postForEntity(
                baseUrl() + "/refresh",
                new RefreshTokenRequest(login.refreshToken()),
                AuthResponse.class);
        assertThat(refreshed.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(refreshed.getBody()).isNotNull();
        assertThat(refreshed.getBody().refreshToken()).isNotEqualTo(login.refreshToken());

        ResponseEntity<ErrorResponse> reuseAttempt = restTemplate.postForEntity(
                baseUrl() + "/refresh",
                new RefreshTokenRequest(login.refreshToken()),
                ErrorResponse.class);
        assertThat(reuseAttempt.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    void should_revokeRefreshToken_when_loggingOut() {
        seedUser("logout-ok@example.com", "correct-horse-battery-staple");
        AuthResponse login = restTemplate.postForEntity(
                baseUrl() + "/login",
                new LoginRequest("logout-ok@example.com", "correct-horse-battery-staple"),
                AuthResponse.class).getBody();

        ResponseEntity<Void> logoutResponse = restTemplate.postForEntity(
                baseUrl() + "/logout",
                new RefreshTokenRequest(login.refreshToken()),
                Void.class);
        assertThat(logoutResponse.getStatusCode()).isEqualTo(HttpStatus.NO_CONTENT);

        ResponseEntity<ErrorResponse> reuseAttempt = restTemplate.postForEntity(
                baseUrl() + "/refresh",
                new RefreshTokenRequest(login.refreshToken()),
                ErrorResponse.class);
        assertThat(reuseAttempt.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
    }

    @Test
    void should_lockAccount_when_fiveConsecutiveLoginFailuresOccur() {
        seedUser("lockout@example.com", "correct-horse-battery-staple");

        for (int i = 0; i < 5; i++) {
            restTemplate.postForEntity(
                    baseUrl() + "/login",
                    new LoginRequest("lockout@example.com", "wrong-password"),
                    ErrorResponse.class);
        }

        ResponseEntity<ErrorResponse> lockedAttempt = restTemplate.postForEntity(
                baseUrl() + "/login",
                new LoginRequest("lockout@example.com", "correct-horse-battery-staple"),
                ErrorResponse.class);

        assertThat(lockedAttempt.getStatusCode()).isEqualTo(HttpStatus.UNAUTHORIZED);
        assertThat(lockedAttempt.getBody()).isNotNull();
        assertThat(lockedAttempt.getBody().message()).contains("locked");
    }
}

That's the complete set of changed/added files for this correction pass — full Security/Identity backend implementation (entities, repositories, JWT issuance/validation, login/refresh/logout with server-side refresh-token revocation, failed-attempt lockout, AES-GCM PII-encryption scaffolding, exception handling, and tests), plus the `application.yml` fix removing the `SNAKE_CASE` Jackson override and a `README.md` update reflecting the refresh-token store and lockout behavior. `pom.xml` and `.env.example` needed no changes and are omitted.
