package com.insider.controller;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.insider.dto.request.InsightCreateRequest;
import com.insider.dto.request.InsightUpdateRequest;
import com.insider.entity.Insight;
import com.insider.entity.Role;
import com.insider.entity.Source;
import com.insider.entity.User;
import com.insider.repository.InsightRepository;
import com.insider.repository.UserRepository;
import com.insider.security.JwtProvider;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Nested;
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
class InsightControllerTest {

    private static final String INSIGHTS_ENDPOINT = "/api/v1/insights";
    private static final String TEST_TITLE = "Test Insight";
    private static final String TEST_DESCRIPTION = "Test description";

    @Autowired private MockMvc mockMvc;

    @Autowired private ObjectMapper objectMapper;

    @Autowired private UserRepository userRepository;

    @Autowired private InsightRepository insightRepository;

    @Autowired private PasswordEncoder passwordEncoder;

    @Autowired private JwtProvider jwtProvider;

    private User testUser;
    private User otherUser;
    private String authToken;
    private String otherAuthToken;

    @BeforeEach
    void setUp() {
        insightRepository.deleteAll();
        userRepository.deleteAll();

        testUser =
                new User(
                        UUID.randomUUID(),
                        "test@example.com",
                        "Test User",
                        passwordEncoder.encode("password123"),
                        Role.ADVOCATE);
        userRepository.save(testUser);
        authToken = jwtProvider.generateToken(testUser.getEmail());

        otherUser =
                new User(
                        UUID.randomUUID(),
                        "other@example.com",
                        "Other User",
                        passwordEncoder.encode("password123"),
                        Role.PRODUCT_MANAGER);
        userRepository.save(otherUser);
        otherAuthToken = jwtProvider.generateToken(otherUser.getEmail());
    }

    @Nested
    class ListInsights {
        @Test
        void listInsights_Empty_ReturnsEmptyList() throws Exception {
            mockMvc.perform(get(INSIGHTS_ENDPOINT).header("Authorization", "Bearer " + authToken))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.items").isArray())
                    .andExpect(jsonPath("$.items").isEmpty())
                    .andExpect(jsonPath("$.total").value(0))
                    .andExpect(jsonPath("$.limit").value(20))
                    .andExpect(jsonPath("$.offset").value(0));
        }

        @Test
        void listInsights_WithData_ReturnsInsights() throws Exception {
            Insight insight =
                    new Insight(testUser.getId(), TEST_TITLE, TEST_DESCRIPTION, Source.CONFERENCE);
            insightRepository.save(insight);

            mockMvc.perform(get(INSIGHTS_ENDPOINT).header("Authorization", "Bearer " + authToken))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.items[0].title").value(TEST_TITLE))
                    .andExpect(jsonPath("$.items[0].description").value(TEST_DESCRIPTION))
                    .andExpect(jsonPath("$.total").value(1));
        }

        @Test
        void listInsights_WithoutAuth_Returns401() throws Exception {
            mockMvc.perform(get(INSIGHTS_ENDPOINT)).andExpect(status().isUnauthorized());
        }
    }

    @Nested
    class CreateInsight {
        @Test
        void createInsight_Valid_ReturnsCreated() throws Exception {
            InsightCreateRequest request =
                    new InsightCreateRequest(TEST_TITLE, TEST_DESCRIPTION, Source.CONFERENCE);

            mockMvc.perform(
                            post(INSIGHTS_ENDPOINT)
                                    .header("Authorization", "Bearer " + authToken)
                                    .contentType(MediaType.APPLICATION_JSON)
                                    .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isCreated())
                    .andExpect(jsonPath("$.title").value(TEST_TITLE))
                    .andExpect(jsonPath("$.description").value(TEST_DESCRIPTION))
                    .andExpect(jsonPath("$.source").value("conference"))
                    .andExpect(jsonPath("$.id").isNotEmpty());
        }

        @Test
        void createInsight_MissingTitle_Returns422() throws Exception {
            InsightCreateRequest request = new InsightCreateRequest(null, TEST_DESCRIPTION, null);

            mockMvc.perform(
                            post(INSIGHTS_ENDPOINT)
                                    .header("Authorization", "Bearer " + authToken)
                                    .contentType(MediaType.APPLICATION_JSON)
                                    .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isUnprocessableEntity());
        }

        @Test
        void createInsight_EmptyTitle_Returns422() throws Exception {
            InsightCreateRequest request = new InsightCreateRequest("  ", TEST_DESCRIPTION, null);

            mockMvc.perform(
                            post(INSIGHTS_ENDPOINT)
                                    .header("Authorization", "Bearer " + authToken)
                                    .contentType(MediaType.APPLICATION_JSON)
                                    .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isUnprocessableEntity());
        }

        @Test
        void createInsight_TitleTooLong_Returns422() throws Exception {
            String longTitle = "x".repeat(201);
            InsightCreateRequest request = new InsightCreateRequest(longTitle, TEST_DESCRIPTION, null);

            mockMvc.perform(
                            post(INSIGHTS_ENDPOINT)
                                    .header("Authorization", "Bearer " + authToken)
                                    .contentType(MediaType.APPLICATION_JSON)
                                    .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isUnprocessableEntity());
        }

        @Test
        void createInsight_WithoutAuth_Returns401() throws Exception {
            InsightCreateRequest request =
                    new InsightCreateRequest(TEST_TITLE, TEST_DESCRIPTION, null);

            mockMvc.perform(
                            post(INSIGHTS_ENDPOINT)
                                    .contentType(MediaType.APPLICATION_JSON)
                                    .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isUnauthorized());
        }
    }

    @Nested
    class GetInsight {
        @Test
        void getInsight_Found_ReturnsInsight() throws Exception {
            Insight insight =
                    new Insight(testUser.getId(), TEST_TITLE, TEST_DESCRIPTION, Source.CONFERENCE);
            insightRepository.save(insight);

            mockMvc.perform(
                            get(INSIGHTS_ENDPOINT + "/" + insight.getId())
                                    .header("Authorization", "Bearer " + authToken))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.title").value(TEST_TITLE))
                    .andExpect(jsonPath("$.id").value(insight.getId().toString()));
        }

        @Test
        void getInsight_NotFound_Returns404() throws Exception {
            UUID nonExistentId = UUID.randomUUID();

            mockMvc.perform(
                            get(INSIGHTS_ENDPOINT + "/" + nonExistentId)
                                    .header("Authorization", "Bearer " + authToken))
                    .andExpect(status().isNotFound())
                    .andExpect(jsonPath("$.detail").value("Insight not found"));
        }
    }

    @Nested
    class UpdateInsight {
        @Test
        void updateInsight_AsAuthor_ReturnsUpdated() throws Exception {
            Insight insight =
                    new Insight(testUser.getId(), TEST_TITLE, TEST_DESCRIPTION, Source.CONFERENCE);
            insightRepository.save(insight);

            InsightUpdateRequest request =
                    new InsightUpdateRequest("Updated Title", null, null);

            mockMvc.perform(
                            put(INSIGHTS_ENDPOINT + "/" + insight.getId())
                                    .header("Authorization", "Bearer " + authToken)
                                    .contentType(MediaType.APPLICATION_JSON)
                                    .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isOk())
                    .andExpect(jsonPath("$.title").value("Updated Title"))
                    .andExpect(jsonPath("$.description").value(TEST_DESCRIPTION));
        }

        @Test
        void updateInsight_NotFound_Returns404() throws Exception {
            UUID nonExistentId = UUID.randomUUID();
            InsightUpdateRequest request =
                    new InsightUpdateRequest("Updated Title", null, null);

            mockMvc.perform(
                            put(INSIGHTS_ENDPOINT + "/" + nonExistentId)
                                    .header("Authorization", "Bearer " + authToken)
                                    .contentType(MediaType.APPLICATION_JSON)
                                    .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isNotFound());
        }

        @Test
        void updateInsight_AsNonAuthor_Returns403() throws Exception {
            Insight insight =
                    new Insight(testUser.getId(), TEST_TITLE, TEST_DESCRIPTION, Source.CONFERENCE);
            insightRepository.save(insight);

            InsightUpdateRequest request =
                    new InsightUpdateRequest("Updated Title", null, null);

            mockMvc.perform(
                            put(INSIGHTS_ENDPOINT + "/" + insight.getId())
                                    .header("Authorization", "Bearer " + otherAuthToken)
                                    .contentType(MediaType.APPLICATION_JSON)
                                    .content(objectMapper.writeValueAsString(request)))
                    .andExpect(status().isForbidden())
                    .andExpect(jsonPath("$.detail").value("Not authorized to modify this insight"));
        }
    }

    @Nested
    class DeleteInsight {
        @Test
        void deleteInsight_AsAuthor_Returns204() throws Exception {
            Insight insight =
                    new Insight(testUser.getId(), TEST_TITLE, TEST_DESCRIPTION, Source.CONFERENCE);
            insightRepository.save(insight);

            mockMvc.perform(
                            delete(INSIGHTS_ENDPOINT + "/" + insight.getId())
                                    .header("Authorization", "Bearer " + authToken))
                    .andExpect(status().isNoContent());
        }

        @Test
        void deleteInsight_NotFound_Returns404() throws Exception {
            UUID nonExistentId = UUID.randomUUID();

            mockMvc.perform(
                            delete(INSIGHTS_ENDPOINT + "/" + nonExistentId)
                                    .header("Authorization", "Bearer " + authToken))
                    .andExpect(status().isNotFound());
        }

        @Test
        void deleteInsight_AsNonAuthor_Returns403() throws Exception {
            Insight insight =
                    new Insight(testUser.getId(), TEST_TITLE, TEST_DESCRIPTION, Source.CONFERENCE);
            insightRepository.save(insight);

            mockMvc.perform(
                            delete(INSIGHTS_ENDPOINT + "/" + insight.getId())
                                    .header("Authorization", "Bearer " + otherAuthToken))
                    .andExpect(status().isForbidden());
        }
    }
}
