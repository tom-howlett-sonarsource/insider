package com.insider.security;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class JwtProviderTest {

    private static final String TEST_SECRET = "test-secret-key-for-testing-only-minimum-256-bits";
    private static final long EXPIRATION_MINUTES = 30;
    private static final String TEST_EMAIL = "test@example.com";

    private JwtProvider jwtProvider;

    @BeforeEach
    void setUp() {
        jwtProvider = new JwtProvider(TEST_SECRET, EXPIRATION_MINUTES);
    }

    @Test
    void generateToken_CreatesValidToken() {
        String token = jwtProvider.generateToken(TEST_EMAIL);

        assertThat(token).isNotBlank();
        assertThat(jwtProvider.validateToken(token)).isTrue();
    }

    @Test
    void getEmailFromToken_ReturnsCorrectEmail() {
        String token = jwtProvider.generateToken(TEST_EMAIL);

        String email = jwtProvider.getEmailFromToken(token);

        assertThat(email).isEqualTo(TEST_EMAIL);
    }

    @Test
    void validateToken_WithValidToken_ReturnsTrue() {
        String token = jwtProvider.generateToken(TEST_EMAIL);

        assertThat(jwtProvider.validateToken(token)).isTrue();
    }

    @Test
    void validateToken_WithInvalidToken_ReturnsFalse() {
        assertThat(jwtProvider.validateToken("invalid.token.here")).isFalse();
    }

    @Test
    void validateToken_WithTamperedToken_ReturnsFalse() {
        String token = jwtProvider.generateToken(TEST_EMAIL);
        String tamperedToken = token.substring(0, token.length() - 5) + "xxxxx";

        assertThat(jwtProvider.validateToken(tamperedToken)).isFalse();
    }
}
