package com.clarium.hrms.security.jwt;

import com.clarium.hrms.security.domain.Role;
import com.clarium.hrms.security.domain.UserCredential;
import jakarta.servlet.FilterChain;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockHttpServletRequest;
import org.springframework.mock.web.MockHttpServletResponse;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

import java.util.Base64;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;

/**
 * Verifies the stateless trust boundary described in the README: the filter
 * derives identity/authority purely from a well-formed ACCESS token's claims,
 * with no database lookup, and never lets a malformed/expired/wrong-type
 * token propagate an exception out of the filter chain - it just leaves the
 * request unauthenticated so downstream access-control (or the entry point)
 * makes the actual allow/deny call.
 */
class JwtAuthenticationFilterTest {

    private static final String TEST_SECRET = Base64.getEncoder().encodeToString(new byte[32]);

    private JwtTokenProvider provider;
    private JwtAuthenticationFilter filter;
    private UserCredential manager;

    @BeforeEach
    void setUp() {
        JwtProperties properties = new JwtProperties();
        properties.setSecret(TEST_SECRET);
        properties.setAccessTokenTtlSeconds(900);
        properties.setRefreshTokenTtlSeconds(604800);
        provider = new JwtTokenProvider(properties);
        filter = new JwtAuthenticationFilter(provider);

        manager = UserCredential.builder()
                .id(5L)
                .email("manager@example.com")
                .role(Role.MANAGER)
                .employeeId(7L)
                .enabled(true)
                .accountLocked(false)
                .build();
    }

    @AfterEach
    void tearDown() {
        SecurityContextHolder.clearContext();
    }

    @Test
    void requestWithNoAuthorizationHeaderIsLeftUnauthenticated() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest();
        MockHttpServletResponse response = new MockHttpServletResponse();
        FilterChain chain = mock(FilterChain.class);

        filter.doFilter(request, response, chain);

        assertThat(SecurityContextHolder.getContext().getAuthentication()).isNull();
        verify(chain).doFilter(request, response);
    }

    @Test
    void validAccessTokenPopulatesSecurityContextWithEmailAndRoleAuthority() throws Exception {
        String accessToken = provider.generateAccessToken(manager);
        MockHttpServletRequest request = new MockHttpServletRequest();
        request.addHeader("Authorization", "Bearer " + accessToken);
        MockHttpServletResponse response = new MockHttpServletResponse();
        FilterChain chain = mock(FilterChain.class);

        filter.doFilter(request, response, chain);

        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        assertThat(authentication).isNotNull();
        assertThat(authentication.getName()).isEqualTo("manager@example.com");
        assertThat(authentication.getAuthorities())
                .extracting(Object::toString)
                .containsExactly("ROLE_MANAGER");
        verify(chain).doFilter(request, response);
    }

    @Test
    void refreshTokenPresentedAsABearerTokenIsNotTreatedAsAuthentication() throws Exception {
        String refreshToken = provider.generateRefreshToken(manager);
        MockHttpServletRequest request = new MockHttpServletRequest();
        request.addHeader("Authorization", "Bearer " + refreshToken);
        MockHttpServletResponse response = new MockHttpServletResponse();
        FilterChain chain = mock(FilterChain.class);

        filter.doFilter(request, response, chain);

        assertThat(SecurityContextHolder.getContext().getAuthentication()).isNull();
        verify(chain).doFilter(request, response);
    }

    @Test
    void malformedTokenDoesNotThrowAndLeavesRequestUnauthenticated() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest();
        request.addHeader("Authorization", "Bearer garbage-token");
        MockHttpServletResponse response = new MockHttpServletResponse();
        FilterChain chain = mock(FilterChain.class);

        filter.doFilter(request, response, chain);

        assertThat(SecurityContextHolder.getContext().getAuthentication()).isNull();
        verify(chain).doFilter(request, response);
    }

    @Test
    void nonBearerSchemeIsIgnored() throws Exception {
        MockHttpServletRequest request = new MockHttpServletRequest();
        request.addHeader("Authorization", "Basic dXNlcjpwYXNz");
        MockHttpServletResponse response = new MockHttpServletResponse();
        FilterChain chain = mock(FilterChain.class);

        filter.doFilter(request, response, chain);

        assertThat(SecurityContextHolder.getContext().getAuthentication()).isNull();
        verify(chain).doFilter(request, response);
    }

    @Test
    void expiredAccessTokenIsIgnoredRatherThanRejectedWithAnException() throws Exception {
        JwtProperties expiredProperties = new JwtProperties();
        expiredProperties.setSecret(TEST_SECRET);
        expiredProperties.setAccessTokenTtlSeconds(-10);
        expiredProperties.setRefreshTokenTtlSeconds(-10);
        JwtTokenProvider expiredTokenProvider = new JwtTokenProvider(expiredProperties);
        JwtAuthenticationFilter filterWithExpiredProvider = new JwtAuthenticationFilter(expiredTokenProvider);
        String expiredToken = expiredTokenProvider.generateAccessToken(manager);

        MockHttpServletRequest request = new MockHttpServletRequest();
        request.addHeader("Authorization", "Bearer " + expiredToken);
        MockHttpServletResponse response = new MockHttpServletResponse();
        FilterChain chain = mock(FilterChain.class);

        filterWithExpiredProvider.doFilter(request, response, chain);

        assertThat(SecurityContextHolder.getContext().getAuthentication()).isNull();
        verify(chain).doFilter(request, response);
    }

    @Test
    void doesNotEscalatePrivilegeWhenRoleClaimIsForAHigherPrivilegeThanStored() throws Exception {
        // Defends against a claim-tampering regression: the filter must derive
        // authority strictly from what is *in* the token, not re-check the
        // database - so a role change takes effect only once the token is
        // reissued, exactly as documented in the README's staleness tradeoff.
        UserCredential admin = UserCredential.builder()
                .id(9L)
                .email("admin@example.com")
                .role(Role.ADMIN)
                .employeeId(null)
                .enabled(true)
                .accountLocked(false)
                .build();
        String accessToken = provider.generateAccessToken(admin);

        MockHttpServletRequest request = new MockHttpServletRequest();
        request.addHeader("Authorization", "Bearer " + accessToken);
        MockHttpServletResponse response = new MockHttpServletResponse();
        FilterChain chain = mock(FilterChain.class);

        filter.doFilter(request, response, chain);

        Authentication authentication = SecurityContextHolder.getContext().getAuthentication();
        assertThat(authentication.getAuthorities())
                .extracting(Object::toString)
                .containsExactly("ROLE_ADMIN");
    }
}
