package com.clarium.hrms.security.jwt;

import com.clarium.hrms.security.domain.UserCredential;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.io.Decoders;
import io.jsonwebtoken.security.Keys;
import jakarta.annotation.PostConstruct;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.time.Instant;
import java.util.Date;
import java.util.Optional;

@Component
@RequiredArgsConstructor
public class JwtTokenProvider {

    private static final int MINIMUM_KEY_LENGTH_BYTES = 32;
    private static final String CLAIM_EMPLOYEE_ID = "employeeId";
    private static final String CLAIM_ROLE = "role";
    private static final String CLAIM_TYPE = "type";

    private final JwtProperties jwtProperties;

    private SecretKey signingKey;

    @PostConstruct
    void init() {
        byte[] keyBytes = Decoders.BASE64.decode(jwtProperties.secret());
        if (keyBytes.length < MINIMUM_KEY_LENGTH_BYTES) {
            throw new IllegalStateException(
                    "app.security.jwt.secret must decode to at least 256 bits; generate one with `openssl rand -base64 32`");
        }
        signingKey = Keys.hmacShaKeyFor(keyBytes);
    }

    public String generateToken(UserCredential credential, TokenType type) {
        Instant now = Instant.now();
        long ttlSeconds = type == TokenType.ACCESS
                ? jwtProperties.accessTokenTtlSeconds()
                : jwtProperties.refreshTokenTtlSeconds();

        return Jwts.builder()
                .subject(credential.getEmail())
                .claim(CLAIM_EMPLOYEE_ID, credential.getEmployeeId())
                .claim(CLAIM_ROLE, credential.getRole().name())
                .claim(CLAIM_TYPE, type.name())
                .issuedAt(Date.from(now))
                .expiration(Date.from(now.plusSeconds(ttlSeconds)))
                .signWith(signingKey)
                .compact();
    }

    public Optional<Claims> parseClaims(String token, TokenType expectedType) {
        try {
            Claims claims = Jwts.parser()
                    .verifyWith(signingKey)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();
            if (!expectedType.name().equals(claims.get(CLAIM_TYPE, String.class))) {
                return Optional.empty();
            }
            return Optional.of(claims);
        } catch (JwtException | IllegalArgumentException e) {
            return Optional.empty();
        }
    }

    public Optional<String> parseSubject(String token, TokenType expectedType) {
        return parseClaims(token, expectedType).map(Claims::getSubject);
    }
}
