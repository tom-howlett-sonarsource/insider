package com.insider.controller;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.insider.dto.request.LoginRequest;
import com.insider.entity.Role;
import com.insider.entity.User;
import com.insider.repository.UserRepository;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.transaction.annotation.Transactional;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Transactional
class AuthControllerTest {

    private static final String LOGIN_ENDPOINT = "/api/v1/auth/login";
    private static final String TEST_EMAIL = "test@example.com";
    private static final String TEST_PASSWORD = "password123";

    @Autowired private MockMvc mockMvc;

    @Autowired private ObjectMapper objectMapper;

    @Autowired private UserRepository userRepository;

    @Autowired private PasswordEncoder passwordEncoder;

    @BeforeEach
    void setUp() {
        userRepository.deleteAll();
        User user =
                new User(
                        UUID.randomUUID(),
                        TEST_EMAIL,
                        "Test User",
                        passwordEncoder.encode(TEST_PASSWORD),
                        Role.ADVOCATE);
        userRepository.save(user);
    }

    @Test
    void login_WithValidCredentials_ReturnsToken() throws Exception {
        LoginRequest request = new LoginRequest(TEST_EMAIL, TEST_PASSWORD);

        mockMvc.perform(
                        post(LOGIN_ENDPOINT)
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.access_token").isNotEmpty())
                .andExpect(jsonPath("$.token_type").value("bearer"));
    }

    @Test
    void login_WithInvalidPassword_Returns401() throws Exception {
        LoginRequest request = new LoginRequest(TEST_EMAIL, "wrongpassword");

        mockMvc.perform(
                        post(LOGIN_ENDPOINT)
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.detail").value("Invalid email or password"));
    }

    @Test
    void login_WithUnknownUser_Returns401() throws Exception {
        LoginRequest request = new LoginRequest("unknown@example.com", TEST_PASSWORD);

        mockMvc.perform(
                        post(LOGIN_ENDPOINT)
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isUnauthorized())
                .andExpect(jsonPath("$.detail").value("Invalid email or password"));
    }

    @Test
    void login_WithMissingEmail_Returns422() throws Exception {
        String request = "{\"password\": \"password123\"}";

        mockMvc.perform(
                        post(LOGIN_ENDPOINT)
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(request))
                .andExpect(status().isUnprocessableEntity());
    }

    @Test
    void login_WithInvalidEmailFormat_Returns422() throws Exception {
        LoginRequest request = new LoginRequest("notanemail", TEST_PASSWORD);

        mockMvc.perform(
                        post(LOGIN_ENDPOINT)
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(objectMapper.writeValueAsString(request)))
                .andExpect(status().isUnprocessableEntity());
    }
}
