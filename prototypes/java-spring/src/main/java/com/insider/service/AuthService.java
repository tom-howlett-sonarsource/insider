package com.insider.service;

import com.insider.dto.request.LoginRequest;
import com.insider.dto.response.TokenResponse;
import com.insider.entity.User;
import com.insider.repository.UserRepository;
import com.insider.security.JwtProvider;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

/**
 * Service for authentication operations.
 */
@Service
public class AuthService {

    private static final String INVALID_CREDENTIALS = "Invalid email or password";

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtProvider jwtProvider;

    public AuthService(
            UserRepository userRepository,
            PasswordEncoder passwordEncoder,
            JwtProvider jwtProvider) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtProvider = jwtProvider;
    }

    /**
     * Authenticate user and return JWT token.
     *
     * @throws BadCredentialsException if credentials are invalid
     */
    public TokenResponse login(LoginRequest request) {
        User user =
                userRepository
                        .findByEmail(request.email())
                        .orElseThrow(() -> new BadCredentialsException(INVALID_CREDENTIALS));

        if (!passwordEncoder.matches(request.password(), user.getHashedPassword())) {
            throw new BadCredentialsException(INVALID_CREDENTIALS);
        }

        String token = jwtProvider.generateToken(user.getEmail());
        return new TokenResponse(token);
    }
}
