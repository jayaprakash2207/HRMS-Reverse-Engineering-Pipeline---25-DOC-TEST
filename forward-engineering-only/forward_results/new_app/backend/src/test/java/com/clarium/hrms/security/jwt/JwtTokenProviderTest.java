package com.clarium.hrms.security.jwt;

import com.clarium.hrms.security.domain.Role;
import com.clarium.hrms.security.domain.UserCredential;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.MalformedJwtException;
import io.jsonwebtoken.security.SignatureException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Base64;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class JwtTokenProviderTest {

    // 32 zero bytes - deterministic, satisfies the >=256-bit HMAC key requirement
    // for test purposes only. Never reused as a real secret.
    private static final String TEST_SECRET = Base64.getEncoder().encodeToString(new byte[32]);

    private JwtTokenProvider provider;
    private UserCredential employee;
    private UserCredential hrAdminWithoutEmployeeRecord;

    @BeforeEach
    void setUp() {
        JwtProperties properties = new JwtProperties();
        properties.setSecret(TEST_SECRET);
        properties.setAccessTokenTtlSeconds(900);
        properties.setRefreshTokenTtlSeconds(604800);
        provider = new JwtTokenProvider(properties);

        employee = UserCredential.builder()
                .id(1L)
                .email("jane.doe@example.com")
                .role(Role.EMPLOYEE)
                .employeeId(42L)
                .enabled(true)
                .accountLocked(false)
                .build();

        // HR admins are not necessarily backed by an EMPLOYEES row - employeeId must
        // round-trip as null rather than blow up serialization.
        hrAdminWithoutEmployeeRecord = UserCredential.builder()
                .id(2L)
                .email("hr.admin@example.com")
                .role(Role.HR_ADMIN)
                .employeeId(null)
                .enabled(true)
                .accountLocked(false)
                .build();
    }

    @Test
    void accessTokenCarriesEmailRoleAndEmployeeIdClaims() {
        String token = provider.generateAccessToken(employee);
        Claims claims = provider.parseClaims(token);

        assertThat(provider.getTokenType(claims)).isEqualTo(TokenType.ACCESS);
        assertThat(provider.getEmail(claims)).isEqualTo("jane.doe@example.com");
        assertThat(provider.getRole(claims)).isEqualTo(Role.EMPLOYEE);
        assertThat(provider.getEmployeeId(claims)).isEqualTo(42L);
    }

    @Test
    void refreshTokenIsDistinguishableFromAccessToken() {
        String token = provider.generateRefreshToken(employee);
        Claims claims = provider.parseClaims(token);

        assertThat(provider.getTokenType(claims)).isEqualTo(TokenType.REFRESH);
        assertThat(provider.getEmail(claims)).isEqualTo("jane.doe@example.com");
    }

    @Test
    void nullEmployeeIdRoundTripsAsNull() {
        String token = provider.generateAccessToken(hrAdminWithoutEmployeeRecord);
        Claims claims = provider.parseClaims(token);

        assertThat(provider.getEmployeeId(claims)).isNull();
        assertThat(provider.getRole(claims)).isEqualTo(Role.HR_ADMIN);
    }

    @Test
    void accessAndRefreshTokensForTheSameUserAreNotInterchangeableStrings() {
        String accessToken = provider.generateAccessToken(employee);
        String refreshToken = provider.generateRefreshToken(employee);

        assertThat(accessToken).isNotEqualTo(refreshToken);
    }

    @Test
    void expiredTokenFailsToParse() {
        JwtProperties expiredProperties = new JwtProperties();
        expiredProperties.setSecret(TEST_SECRET);
        expiredProperties.setAccessTokenTtlSeconds(-10);
        expiredProperties.setRefreshTokenTtlSeconds(-10);
        JwtTokenProvider expiredTokenProvider = new JwtTokenProvider(expiredProperties);

        String token = expiredTokenProvider.generateAccessToken(employee);

        assertThatThrownBy(() -> expiredTokenProvider.parseClaims(token))
                .isInstanceOf(ExpiredJwtException.class);
    }

    @Test
    void tokenSignedWithADifferentSecretFailsSignatureValidation() {
        JwtProperties otherProperties = new JwtProperties();
        otherProperties.setSecret(Base64.getEncoder().encodeToString(new byte[]{
                1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32
        }));
        otherProperties.setAccessTokenTtlSeconds(900);
        otherProperties.setRefreshTokenTtlSeconds(604800);
        JwtTokenProvider otherProvider = new JwtTokenProvider(otherProperties);

        String tokenSignedByOtherSecret = otherProvider.generateAccessToken(employee);

        assertThatThrownBy(() -> provider.parseClaims(tokenSignedByOtherSecret))
                .isInstanceOf(SignatureException.class);
    }

    @Test
    void malformedTokenStringFailsToParse() {
        assertThatThrownBy(() -> provider.parseClaims("not-a-valid-jwt"))
                .isInstanceOf(MalformedJwtException.class);
    }

    @Test
    void accessTokenTtlIsExposedForCallersThatBuildTheAuthResponse() {
        assertThat(provider.getAccessTokenTtlSeconds()).isEqualTo(900L);
    }
}
