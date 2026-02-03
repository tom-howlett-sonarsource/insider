package com.insider.controller;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.insider.entity.Role;
import com.insider.entity.User;
import com.insider.repository.UserRepository;
import com.insider.security.JwtProvider;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
class UserControllerTest {

    private static final String ME_ENDPOINT = "/api/v1/users/me";
    private static final String TEST_EMAIL = "test@example.com";
    private static final String TEST_NAME = "Test User";

    @Autowired private MockMvc mockMvc;

    @Autowired private UserRepository userRepository;

    @Autowired private PasswordEncoder passwordEncoder;

    @Autowired private JwtProvider jwtProvider;

    private User testUser;
    private String authToken;

    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
        testUser =
                new User(
                        UUID.randomUUID(),
                        TEST_EMAIL,
                        TEST_NAME,
                        passwordEncoder.encode("password123"),
                        Role.ADVOCATE);
        userRepository.save(testUser);
        authToken = jwtProvider.generateToken(TEST_EMAIL);
    }

    @Test
    void getMe_WithValidToken_ReturnsUser() throws Exception {
        mockMvc.perform(get(ME_ENDPOINT).header("Authorization", "Bearer " + authToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(testUser.getId().toString()))
                .andExpect(jsonPath("$.email").value(TEST_EMAIL))
                .andExpect(jsonPath("$.name").value(TEST_NAME))
                .andExpect(jsonPath("$.role").value("advocate"));
    }

    @Test
    void getMe_WithoutToken_Returns401() throws Exception {
        mockMvc.perform(get(ME_ENDPOINT)).andExpect(status().isUnauthorized());
    }

    @Test
    void getMe_WithInvalidToken_Returns401() throws Exception {
        mockMvc.perform(get(ME_ENDPOINT).header("Authorization", "Bearer invalid-token"))
                .andExpect(status().isUnauthorized());
    }
}
